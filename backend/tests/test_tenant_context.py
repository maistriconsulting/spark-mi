from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.dependencies import get_tenant_context
from app.core.security import create_access_token, hash_password
from app.models import Membership, Tenant, User


def test_tenant_context_requires_active_membership():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        user = User(email="analyst@example.test", full_name="Analyst", password_hash=hash_password("a-long-test-password"))
        tenant = Tenant(name="Tenant A", slug="tenant-a")
        db.add_all([user, tenant])
        db.flush()
        membership = Membership(user_id=user.id, tenant_id=tenant.id, role="analyst", status="active")
        db.add(membership)
        db.commit()

        token = create_access_token(user_id=user.id, tenant_id=tenant.id)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        ctx = get_tenant_context(user=user, credentials=credentials, db=db)
        assert ctx.tenant_id == tenant.id
        assert ctx.role == "analyst"

        membership.status = "revoked"
        db.commit()
        try:
            get_tenant_context(user=user, credentials=credentials, db=db)
            assert False, "revoked membership must not grant tenant access"
        except Exception as exc:
            assert getattr(exc, "status_code", None) == 403
