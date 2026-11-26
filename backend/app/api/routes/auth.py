from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core import audit
from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_superadmin, get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Membership, Tenant, User
from app.schemas.auth import (
    BootstrapRequest, BootstrapStatusResponse, ChangePasswordRequest, LoginRequest, PlatformOverviewResponse,
    SelectTenantRequest, TenantSummary, TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/bootstrap", response_model=TokenResponse, status_code=201)
def bootstrap(
    payload: BootstrapRequest,
    bootstrap_token: str | None = Header(default=None, alias="X-Bootstrap-Token"),
    db: Session = Depends(get_db),
):
    if not settings.bootstrap_token or bootstrap_token != settings.bootstrap_token:
        raise HTTPException(status_code=404, detail="Not found")
    if db.query(Tenant).first() or db.query(User).first():
        raise HTTPException(status_code=409, detail="Initial setup has already been completed")
    email = payload.email.lower()
    if email != "info@maistriconsulting.com":
        raise HTTPException(status_code=422, detail="The initial superadmin email is fixed")
    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=email,
        full_name="SPARK-MI Superadmin",
        password_hash=hash_password(payload.password),
        is_superadmin=True,
    )
    db.add(user)
    db.flush()
    db.commit()
    return TokenResponse(access_token=create_access_token(user_id=user.id, is_superadmin=True), is_superadmin=True)


@router.get("/bootstrap-status", response_model=BootstrapStatusResponse)
def bootstrap_status(db: Session = Depends(get_db)):
    return BootstrapStatusResponse(initialized=bool(db.query(User.id).first() or db.query(Tenant.id).first()))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == payload.email.lower()).first()
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password incorrect")
    return TokenResponse(access_token=create_access_token(user_id=user.id, is_superadmin=user.is_superadmin), is_superadmin=user.is_superadmin)


@router.get("/tenants", response_model=list[TenantSummary])
def list_tenants(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(Tenant, Membership.role)
        .join(Membership, Membership.tenant_id == Tenant.id)
        .filter(Membership.user_id == user.id, Membership.status == "active", Tenant.status == "active")
        .all()
    )
    return [TenantSummary(id=t.id, name=t.name, slug=t.slug, role=role) for t, role in rows]


@router.post("/select-tenant", response_model=TokenResponse)
def select_tenant(
    payload: SelectTenantRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = (
        db.query(Membership)
        .join(Tenant, Tenant.id == Membership.tenant_id)
        .filter(Membership.user_id == user.id, Membership.tenant_id == payload.tenant_id,
                Membership.status == "active", Tenant.status == "active")
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=403, detail="You are not a member of this organization")
    return TokenResponse(access_token=create_access_token(user_id=user.id, tenant_id=payload.tenant_id, is_superadmin=user.is_superadmin), is_superadmin=user.is_superadmin)


@router.post("/change-password", status_code=204)
def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 400, not 401: a typo here must not end the session.
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="La password attuale non è corretta")
    user.password_hash = hash_password(payload.new_password)
    audit.record(db, user, "user.change_password", "user", user.id, email=user.email)
    db.commit()


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "full_name": user.full_name, "is_superadmin": user.is_superadmin}


@router.get("/platform/overview", response_model=PlatformOverviewResponse)
def platform_overview(superadmin: User = Depends(get_current_superadmin), db: Session = Depends(get_db)):
    tenants = db.query(Tenant).filter(Tenant.status == "active").order_by(Tenant.id).all()
    return PlatformOverviewResponse(
        user_count=db.query(User).count(),
        tenant_count=len(tenants),
        tenants=[TenantSummary(id=t.id, name=t.name, slug=t.slug, role="platform") for t in tenants],
    )
