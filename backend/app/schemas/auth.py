from pydantic import BaseModel, EmailStr, Field


class BootstrapRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SelectTenantRequest(BaseModel):
    tenant_id: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_superadmin: bool = False


class TenantSummary(BaseModel):
    id: int
    name: str
    slug: str
    role: str

    model_config = {"from_attributes": True}


class BootstrapStatusResponse(BaseModel):
    initialized: bool


class PlatformOverviewResponse(BaseModel):
    user_count: int
    tenant_count: int
    tenants: list[TenantSummary]
