from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import jwt

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import Membership, Tenant, User

bearer_scheme = HTTPBearer(auto_error=True)


@dataclass(frozen=True)
class TenantContext:
    user: User
    tenant_id: int
    role: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(credentials.credentials)
        if payload.get("type") != "access" or not payload.get("sub"):
            raise unauthorized
        user = db.get(User, int(payload["sub"]))
    except (jwt.PyJWTError, ValueError, TypeError):
        raise unauthorized
    if user is None or not user.is_active:
        raise unauthorized
    return user


def get_tenant_context(
    user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> TenantContext:
    try:
        payload = decode_access_token(credentials.credentials)
        tenant_id = int(payload["tenant_id"])
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        raise HTTPException(status_code=403, detail="Select an organization before accessing this resource")

    membership = (
        db.query(Membership)
        .join(Tenant, Tenant.id == Membership.tenant_id)
        .filter(Membership.user_id == user.id, Membership.tenant_id == tenant_id,
                Membership.status == "active", Tenant.status == "active")
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=403, detail="You are not an active member of this organization")
    return TenantContext(user=user, tenant_id=tenant_id, role=membership.role)


def get_current_superadmin(user: User = Depends(get_current_user)) -> User:
    # Use the database value, not the JWT claim, so privilege revocation is immediate.
    if not user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin privileges required")
    return user
