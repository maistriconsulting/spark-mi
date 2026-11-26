"""Management API through real HTTP requests, so routing, auth and validation are exercised."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models import AuditEvent, User

API = "/api/v1"
ADMIN = "admin@example.com"
PASSWORD = "a-long-test-password"


@pytest.fixture
def env():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)

    def override():
        with Session(engine, expire_on_commit=False, autoflush=False) as session:
            yield session

    app.dependency_overrides[get_db] = override
    with Session(engine) as db:
        db.add(User(email=ADMIN, full_name="Admin", password_hash=hash_password(PASSWORD), is_superadmin=True))
        db.commit()
    client = TestClient(app)
    yield client, engine
    app.dependency_overrides.clear()


def auth(client, email, password):
    response = client.post(f"{API}/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": "Bearer " + response.json()["access_token"]}


def make_tenant(client, headers, slug="acme"):
    response = client.post(f"{API}/platform/tenants", json={"name": slug.title(), "slug": slug}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def make_user(client, headers, email):
    response = client.post(f"{API}/platform/users", json={"email": email, "full_name": "Test User"}, headers=headers)
    assert response.status_code == 201, response.text
    body = response.json()
    assert "password_hash" not in response.text
    return body["user"]["id"], body["temporary_password"]


def member(client, headers, tenant_id, user_id, role, status="active"):
    return client.put(f"{API}/platform/tenants/{tenant_id}/members/{user_id}",
                      json={"role": role, "status": status}, headers=headers)


def tenant_auth(client, headers, tenant_id):
    response = client.post(f"{API}/auth/select-tenant", json={"tenant_id": tenant_id}, headers=headers)
    return response.status_code, {"Authorization": "Bearer " + response.json().get("access_token", "")}


def test_every_platform_route_requires_superadmin(env):
    client, _ = env
    admin = auth(client, ADMIN, PASSWORD)
    tenant = make_tenant(client, admin)
    user_id, password = make_user(client, admin, "owner@example.com")
    assert member(client, admin, tenant, user_id, "owner").status_code == 200
    owner = auth(client, "owner@example.com", password)

    routes = [(method.upper(), path) for path, operations in app.openapi()["paths"].items()
              if path.startswith(f"{API}/platform") for method in operations]
    assert len(routes) >= 9
    for method, path in routes:
        url = path.replace("{tenant_id}", str(tenant)).replace("{user_id}", str(user_id))
        assert client.request(method, url, headers=owner, json={}).status_code == 403, (method, path)
        assert client.request(method, url, json={}).status_code in {401, 403}, (method, path)


def test_roles_validation_duplicates_and_email_normalisation(env):
    client, _ = env
    admin = auth(client, ADMIN, PASSWORD)
    tenant = make_tenant(client, admin)
    user_id, password = make_user(client, admin, "Mixed.Case@Example.com")
    auth(client, "mixed.case@example.com", password)
    assert client.post(f"{API}/platform/users", json={"email": "mixed.case@example.com", "full_name": "Dup"},
                       headers=admin).status_code == 409
    assert client.post(f"{API}/platform/tenants", json={"name": "Other", "slug": "acme"},
                       headers=admin).status_code == 409
    assert member(client, admin, tenant, user_id, "superadmin").status_code == 422
    assert member(client, admin, 999, user_id, "viewer").status_code == 404
    assert member(client, admin, tenant, user_id, "viewer", "revoked").status_code == 404


def test_superadmin_flag_cannot_be_set_and_superadmin_is_protected(env):
    client, _ = env
    admin = auth(client, ADMIN, PASSWORD)
    response = client.post(f"{API}/platform/users", headers=admin,
                           json={"email": "x@example.com", "full_name": "X User", "is_superadmin": True})
    assert response.json()["user"]["is_superadmin"] is False
    user_id = response.json()["user"]["id"]
    patched = client.patch(f"{API}/platform/users/{user_id}", json={"is_superadmin": True}, headers=admin)
    assert patched.json()["is_superadmin"] is False
    me = client.get(f"{API}/auth/me", headers=admin).json()["id"]
    assert client.patch(f"{API}/platform/users/{me}", json={"is_active": False}, headers=admin).status_code == 409
    assert client.post(f"{API}/platform/users/{me}/reset-password", headers=admin).status_code == 409


def test_role_enforcement_and_last_owner_guard(env):
    client, _ = env
    admin = auth(client, ADMIN, PASSWORD)
    tenant = make_tenant(client, admin)
    first, first_pw = make_user(client, admin, "first@example.com")
    second, _ = make_user(client, admin, "second@example.com")
    assert member(client, admin, tenant, first, "owner").status_code == 200
    assert member(client, admin, tenant, first, "viewer").status_code == 409
    assert member(client, admin, tenant, first, "owner", "revoked").status_code == 409
    assert member(client, admin, tenant, second, "owner").status_code == 200
    assert member(client, admin, tenant, first, "viewer").status_code == 200
    assert member(client, admin, tenant, second, "admin").status_code == 409

    status, scoped = tenant_auth(client, auth(client, "first@example.com", first_pw), tenant)
    assert status == 200
    assert client.get(f"{API}/projects", headers=scoped).status_code == 200
    project = {"name": "Progetto", "slug": "progetto"}
    assert client.post(f"{API}/projects", json=project, headers=scoped).status_code == 403
    assert member(client, admin, tenant, first, "analyst").status_code == 200
    assert client.post(f"{API}/projects", json=project, headers=scoped).status_code == 201


def test_suspension_revocation_and_deactivation_cut_access_immediately(env):
    client, _ = env
    admin = auth(client, ADMIN, PASSWORD)
    tenant = make_tenant(client, admin)
    user_id, password = make_user(client, admin, "analyst@example.com")
    member(client, admin, tenant, user_id, "analyst")
    user = auth(client, "analyst@example.com", password)
    _, scoped = tenant_auth(client, user, tenant)

    def set_tenant(status):
        assert client.patch(f"{API}/platform/tenants/{tenant}", json={"status": status},
                            headers=admin).status_code == 200

    set_tenant("suspended")
    assert client.get(f"{API}/projects", headers=scoped).status_code == 403
    assert tenant_auth(client, user, tenant)[0] == 403
    assert client.get(f"{API}/auth/tenants", headers=user).json() == []
    set_tenant("active")
    assert client.get(f"{API}/projects", headers=scoped).status_code == 200

    member(client, admin, tenant, user_id, "analyst", "revoked")
    assert client.get(f"{API}/projects", headers=scoped).status_code == 403
    member(client, admin, tenant, user_id, "analyst")
    assert client.get(f"{API}/projects", headers=scoped).status_code == 200

    client.patch(f"{API}/platform/users/{user_id}", json={"is_active": False}, headers=admin)
    assert client.get(f"{API}/projects", headers=scoped).status_code == 401


def test_password_reset_change_and_audit_without_secrets(env):
    client, engine = env
    admin = auth(client, ADMIN, PASSWORD)
    user_id, old = make_user(client, admin, "reset@example.com")
    new = client.post(f"{API}/platform/users/{user_id}/reset-password", headers=admin).json()["temporary_password"]
    assert client.post(f"{API}/auth/login", json={"email": "reset@example.com", "password": old}).status_code == 401
    user = auth(client, "reset@example.com", new)
    change = f"{API}/auth/change-password"
    assert client.post(change, headers=user, json={"current_password": "wrong", "new_password": PASSWORD}).status_code == 400
    assert client.post(change, headers=user, json={"current_password": new, "new_password": "short"}).status_code == 422
    assert client.post(change, headers=user, json={"current_password": new, "new_password": PASSWORD}).status_code == 204
    auth(client, "reset@example.com", PASSWORD)

    with Session(engine) as db:
        events = db.query(AuditEvent).all()
        assert [e.action for e in events] == ["user.create", "user.reset_password", "user.change_password"]
        assert not any(secret in e.detail for e in events for secret in (old, new, PASSWORD))
    entries = client.get(f"{API}/platform/audit", headers=admin).json()
    assert entries[-1]["actor_email"] == ADMIN
    assert entries[0]["created_at"].endswith(("Z", "+00:00"))


def test_cors_allows_the_management_methods(env):
    client, _ = env
    from app.core.config import settings
    origin = settings.cors_origin_list[0]
    for method in ("PUT", "PATCH"):
        response = client.options(f"{API}/platform/users/1", headers={
            "Origin": origin, "Access-Control-Request-Method": method})
        assert response.status_code == 200, method
