from datetime import datetime
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,98}[a-z0-9]$")
    description: str | None = Field(default=None, max_length=5000)


class ProjectResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
