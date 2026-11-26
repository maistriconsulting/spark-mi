from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Membership, Tenant, User
from app.schemas.auth import (
    BootstrapRequest, LoginRequest, SelectTenantRequest, TenantSummary, TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/bootstrap", response_model=TokenResponse, status_code=201)
def bootstrap(payload: BootstrapRequest, db: Session = Depends(get_db)):
    if not settings.bootstrap_token or payload.bootstrap_token != settings.bootstrap_token:
        raise HTTPException(status_code=404, detail="Not found")
    if db.query(Tenant).first() or db.query(User).first():
        raise HTTPException(status_code=409, detail="Initial setup has already been completed")
    email = payload.email.lower()
    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(email=email, full_name=payload.full_name, password_hash=hash_password(payload.password))
    tenant = Tenant(name=payload.organization_name, slug=payload.organization_slug)
    db.add_all([user, tenant])
    db.flush()
    db.add(Membership(user_id=user.id, tenant_id=tenant.id, role="owner", status="active"))
    db.commit()
    return TokenResponse(access_token=create_access_token(user_id=user.id, tenant_id=tenant.id))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == payload.email.lower()).first()
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password incorrect")
    return TokenResponse(access_token=create_access_token(user_id=user.id))


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
        .filter_by(user_id=user.id, tenant_id=payload.tenant_id, status="active")
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=403, detail="You are not a member of this organization")
    return TokenResponse(access_token=create_access_token(user_id=user.id, tenant_id=payload.tenant_id))


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "full_name": user.full_name}
