from pydantic import BaseModel, EmailStr, Field


class BootstrapRequest(BaseModel):
    bootstrap_token: str = Field(min_length=24)
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=12, max_length=128)
    organization_name: str = Field(min_length=2, max_length=160)
    organization_slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,78}[a-z0-9]$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SelectTenantRequest(BaseModel):
    tenant_id: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TenantSummary(BaseModel):
    id: int
    name: str
    slug: str
    role: str

    model_config = {"from_attributes": True}
