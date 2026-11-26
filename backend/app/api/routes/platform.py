"""Global administration. Every route requires the database-backed superadmin flag.

Superadmin accounts cannot be created, promoted, deactivated or reset from here.
Nothing is hard-deleted: tenants are suspended, users deactivated, memberships revoked.
"""
import json
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core import audit
from app.core.database import get_db
from app.core.dependencies import get_current_superadmin
from app.core.roles import PROJECT_WRITERS, ROLES
from app.core.security import hash_password
from app.models import AuditEvent, Membership, Tenant, User
from app.schemas.admin import (
    AdminTenant, AdminUser, AuditEntry, MembershipUpdate, RoleInfo, TenantCreate, TenantUpdate,
    UserCreate, UserMembership, UserUpdate, UserWithPassword,
)

router = APIRouter(prefix="/platform", tags=["platform"], dependencies=[Depends(get_current_superadmin)])


def _tenant_view(tenant: Tenant) -> AdminTenant:
    active = [m for m in tenant.memberships if m.status == "active"]
    return AdminTenant(
        id=tenant.id, name=tenant.name, slug=tenant.slug, status=tenant.status, created_at=tenant.created_at,
        member_count=len(active),
        owner_count=sum(1 for m in active if m.role == "owner" and m.user.is_active),
    )


def _user_view(user: User) -> AdminUser:
    return AdminUser(
        id=user.id, email=user.email, full_name=user.full_name, is_active=user.is_active,
        is_superadmin=user.is_superadmin, created_at=user.created_at,
        memberships=[
            UserMembership(tenant_id=m.tenant_id, tenant_name=m.tenant.name, role=m.role, status=m.status)
            for m in sorted(user.memberships, key=lambda m: m.tenant_id)
        ],
    )


def _get(db: Session, model, item_id: int, label: str):
    item = db.get(model, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"{label} non trovato")
    return item


def _commit_unique(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=message)


@router.get("/roles", response_model=list[RoleInfo])
def list_roles():
    return [
        RoleInfo(**role, can_read_projects=True, can_create_projects=role["key"] in PROJECT_WRITERS)
        for role in ROLES
    ]


@router.get("/tenants", response_model=list[AdminTenant])
def list_tenants(db: Session = Depends(get_db)):
    tenants = (
        db.query(Tenant)
        .options(selectinload(Tenant.memberships).selectinload(Membership.user))
        .order_by(Tenant.name)
        .all()
    )
    return [_tenant_view(t) for t in tenants]


@router.post("/tenants", response_model=AdminTenant, status_code=201)
def create_tenant(payload: TenantCreate, actor: User = Depends(get_current_superadmin), db: Session = Depends(get_db)):
    duplicate = "Esiste già un'organizzazione con questo identificativo"
    if db.query(Tenant.id).filter(Tenant.slug == payload.slug).first():
        raise HTTPException(status_code=409, detail=duplicate)
    tenant = Tenant(name=payload.name, slug=payload.slug)
    db.add(tenant)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=duplicate)
    audit.record(db, actor, "tenant.create", "tenant", tenant.id, tenant.id, name=tenant.name, slug=tenant.slug)
    _commit_unique(db, duplicate)
    return _tenant_view(tenant)


@router.patch("/tenants/{tenant_id}", response_model=AdminTenant)
def update_tenant(tenant_id: int, payload: TenantUpdate, actor: User = Depends(get_current_superadmin),
                  db: Session = Depends(get_db)):
    tenant = _get(db, Tenant, tenant_id, "Organizzazione")
    changes = {k: v for k, v in payload.model_dump(exclude_none=True).items() if getattr(tenant, k) != v}
    if changes:
        for key, value in changes.items():
            setattr(tenant, key, value)
        audit.record(db, actor, "tenant.update", "tenant", tenant.id, tenant.id, tenant=tenant.name, **changes)
        db.commit()
    return _tenant_view(tenant)


@router.get("/users", response_model=list[AdminUser])
def list_users(db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .options(selectinload(User.memberships).selectinload(Membership.tenant))
        .order_by(User.email)
        .all()
    )
    return [_user_view(u) for u in users]


@router.post("/users", response_model=UserWithPassword, status_code=201)
def create_user(payload: UserCreate, actor: User = Depends(get_current_superadmin), db: Session = Depends(get_db)):
    duplicate = "Esiste già un utente con questa email"
    email = payload.email.lower()
    if db.query(User.id).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail=duplicate)
    password = secrets.token_urlsafe(15)
    user = User(email=email, full_name=payload.full_name, password_hash=hash_password(password))
    db.add(user)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=duplicate)
    audit.record(db, actor, "user.create", "user", user.id, email=email)
    _commit_unique(db, duplicate)
    return UserWithPassword(user=_user_view(user), temporary_password=password)


@router.patch("/users/{user_id}", response_model=AdminUser)
def update_user(user_id: int, payload: UserUpdate, actor: User = Depends(get_current_superadmin),
                db: Session = Depends(get_db)):
    user = _get(db, User, user_id, "Utente")
    changes = {k: v for k, v in payload.model_dump(exclude_none=True).items() if getattr(user, k) != v}
    if user.is_superadmin and changes.get("is_active") is False:
        raise HTTPException(status_code=409, detail="Un superadmin non può essere disattivato")
    if changes:
        for key, value in changes.items():
            setattr(user, key, value)
        audit.record(db, actor, "user.update", "user", user.id, email=user.email, **changes)
        db.commit()
    return _user_view(user)


@router.post("/users/{user_id}/reset-password", response_model=UserWithPassword)
def reset_password(user_id: int, actor: User = Depends(get_current_superadmin), db: Session = Depends(get_db)):
    user = _get(db, User, user_id, "Utente")
    if user.is_superadmin:
        raise HTTPException(status_code=409, detail="La password di un superadmin si cambia solo dal suo profilo")
    password = secrets.token_urlsafe(15)
    user.password_hash = hash_password(password)
    audit.record(db, actor, "user.reset_password", "user", user.id, email=user.email)
    db.commit()
    return UserWithPassword(user=_user_view(user), temporary_password=password)


@router.put("/tenants/{tenant_id}/members/{user_id}", response_model=AdminUser)
def set_membership(tenant_id: int, user_id: int, payload: MembershipUpdate,
                   actor: User = Depends(get_current_superadmin), db: Session = Depends(get_db)):
    """Add a member, change a role, revoke or restore access."""
    # Lock the tenant row so two concurrent requests cannot both remove an owner.
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).with_for_update().first()
    if tenant is None:
        raise HTTPException(status_code=404, detail="Organizzazione non trovata")
    user = _get(db, User, user_id, "Utente")
    membership = db.query(Membership).filter_by(tenant_id=tenant_id, user_id=user_id).first()
    if membership is None and payload.status != "active":
        raise HTTPException(status_code=404, detail="L'utente non è membro di questa organizzazione")

    loses_ownership = (
        membership is not None and membership.role == "owner" and membership.status == "active"
        and user.is_active and (payload.role != "owner" or payload.status != "active")
    )
    if loses_ownership:
        other_owner = (
            db.query(Membership.id).join(User, User.id == Membership.user_id)
            .filter(Membership.tenant_id == tenant_id, Membership.user_id != user_id,
                    Membership.role == "owner", Membership.status == "active", User.is_active.is_(True))
            .first()
        )
        if other_owner is None:
            raise HTTPException(status_code=409, detail="È l'ultimo owner attivo: assegna prima un altro owner")

    previous = None if membership is None else {"role": membership.role, "status": membership.status}
    if previous != {"role": payload.role, "status": payload.status}:
        if membership is None:
            membership = Membership(tenant_id=tenant_id, user_id=user_id)
            db.add(membership)
        membership.role, membership.status = payload.role, payload.status
        audit.record(db, actor, "membership.set", "user", user.id, tenant_id, email=user.email,
                     tenant=tenant.name, role=payload.role, status=payload.status, previous=previous)
        _commit_unique(db, "L'utente è già membro: ricarica e riprova")
        db.expire(user, ["memberships"])
    return _user_view(user)


@router.get("/audit", response_model=list[AuditEntry])
def list_audit(limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)):
    rows = (
        db.query(AuditEvent, User.email)
        .outerjoin(User, User.id == AuditEvent.actor_user_id)
        .order_by(AuditEvent.id.desc())
        .limit(limit)
        .all()
    )
    return [
        AuditEntry(
            id=e.id, created_at=e.created_at, actor_email=email, action=e.action, target_type=e.target_type,
            target_id=e.target_id, tenant_id=e.tenant_id, detail=json.loads(e.detail),
        )
        for e, email in rows
    ]
