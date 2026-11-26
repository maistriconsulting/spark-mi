from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import TenantContext, get_tenant_context
from app.core.roles import PROJECT_WRITERS
from app.models import Project
from app.schemas.projects import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
def list_projects(ctx: TenantContext = Depends(get_tenant_context), db: Session = Depends(get_db)):
    return db.query(Project).filter(Project.tenant_id == ctx.tenant_id).order_by(Project.id.desc()).all()


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(
    payload: ProjectCreate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: Session = Depends(get_db),
):
    if ctx.role not in PROJECT_WRITERS:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    existing = db.query(Project).filter_by(tenant_id=ctx.tenant_id, slug=payload.slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="Project slug already exists in this organization")
    project = Project(tenant_id=ctx.tenant_id, **payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
