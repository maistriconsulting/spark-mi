from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, EmailStr, Field, StringConstraints

from app.core.roles import Role

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=160)]
# MariaDB returns naive datetimes; they are stored as UTC.
UtcDatetime = Annotated[datetime, AfterValidator(lambda v: v if v.tzinfo else v.replace(tzinfo=timezone.utc))]


class RoleInfo(BaseModel):
    key: Role
    label: str
    purpose: str
    can_read_projects: bool
    can_create_projects: bool


class TenantCreate(BaseModel):
    name: Name
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,78}[a-z0-9]$")


class TenantUpdate(BaseModel):
    name: Name | None = None
    status: Literal["active", "suspended"] | None = None


class AdminTenant(BaseModel):
    id: int
    name: str
    slug: str
    status: str
    created_at: UtcDatetime
    member_count: int
    owner_count: int


class UserCreate(BaseModel):
    email: EmailStr
    full_name: Name


class UserUpdate(BaseModel):
    full_name: Name | None = None
    is_active: bool | None = None


class UserMembership(BaseModel):
    tenant_id: int
    tenant_name: str
    role: str
    status: str


class AdminUser(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    is_superadmin: bool
    created_at: UtcDatetime
    memberships: list[UserMembership]


class UserWithPassword(BaseModel):
    user: AdminUser
    # Returned only by the request that generated it; only the hash is stored.
    temporary_password: str


class MembershipUpdate(BaseModel):
    role: Role
    status: Literal["active", "revoked"] = "active"


class AuditEntry(BaseModel):
    id: int
    created_at: UtcDatetime
    actor_email: str | None
    action: str
    target_type: str
    target_id: int
    tenant_id: int | None
    detail: dict
