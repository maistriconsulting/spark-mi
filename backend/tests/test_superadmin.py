from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.routes.auth import bootstrap, platform_overview
from app.core.config import settings
from app.core.dependencies import get_current_superadmin
from app.core.database import Base
from app.core.security import decode_access_token, hash_password
from app.models import User
from app.schemas.auth import BootstrapRequest


def make_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return Session(engine)


def test_bootstrap_creates_only_the_fixed_global_superadmin(monkeypatch):
    monkeypatch.setattr(settings, "bootstrap_token", "x" * 32)
    with make_db() as db:
        result = bootstrap(
            BootstrapRequest(email="info@maistriconsulting.com", password="a-long-enough-password"),
            bootstrap_token="x" * 32,
            db=db,
        )
        user = db.query(User).one()
        assert user.is_superadmin is True
        assert user.email == "info@maistriconsulting.com"
        assert decode_access_token(result.access_token)["is_superadmin"] is True

        try:
            bootstrap(BootstrapRequest(email="info@maistriconsulting.com", password="a-long-enough-password"), "x" * 32, db)
            assert False, "bootstrap must be one-time"
        except HTTPException as exc:
            assert exc.status_code == 409


def test_superadmin_gate_does_not_grant_tenant_access_to_normal_users():
    with make_db() as db:
        ordinary = User(email="user@example.test", full_name="User", password_hash=hash_password("a-long-test-password"))
        admin = User(email="admin@example.test", full_name="Admin", password_hash=hash_password("a-long-test-password"), is_superadmin=True)
        db.add_all([ordinary, admin])
        db.commit()
        try:
            get_current_superadmin(ordinary)
            assert False, "ordinary user must not be a superadmin"
        except HTTPException as exc:
            assert exc.status_code == 403
        assert get_current_superadmin(admin).id == admin.id
        assert platform_overview(superadmin=admin, db=db).user_count == 2


def test_bootstrap_rejects_other_email_and_short_password(monkeypatch):
    monkeypatch.setattr(settings, "bootstrap_token", "x" * 32)
    with make_db() as db:
        try:
            bootstrap(BootstrapRequest(email="other@maistriconsulting.com", password="a-long-enough-password"), "x" * 32, db)
            assert False, "the initial email must be fixed"
        except HTTPException as exc:
            assert exc.status_code == 422
        try:
            BootstrapRequest(email="info@maistriconsulting.com", password="too-short")
            assert False, "password validation must reject short passwords"
        except ValidationError:
            pass
