# SPARK-MI API

FastAPI backend for the SPARK-MI multi-tenant platform.

## Local setup

Run the following commands from this `backend/` directory:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
```

Edit `.env` with the Hostinger MariaDB connection details and generated secrets. Then apply the migration already included in this repository:

```bash
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## First setup

Call `POST /api/v1/auth/bootstrap` once with the bootstrap token, first owner credentials, and initial organization. Example:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/bootstrap \
  -H 'Content-Type: application/json' \
  -d '{
    "bootstrap_token": "YOUR_BOOTSTRAP_TOKEN",
    "email": "owner@example.com",
    "full_name": "Workspace Owner",
    "password": "A_LONG_UNIQUE_PASSWORD",
    "organization_name": "Example Organization",
    "organization_slug": "example-organization"
  }'
```

The endpoint is disabled after the first user or tenant exists. Remove `BOOTSTRAP_TOKEN` from the environment after successful initialization.

Login returns a user token. Call `GET /api/v1/auth/tenants`, then `POST /api/v1/auth/select-tenant` to receive a tenant-scoped token. Tenant access is revalidated against active membership on every request.

## Hostinger MariaDB

The Fedora host must be explicitly allowed by Hostinger's remote database access controls. Prefer TLS, a dedicated least-privilege database user, a strong password, and a firewall allowlist restricted to the Fedora server's public IP. Never expose MariaDB to all IP addresses. Verify Hostinger's supported TLS settings before production use.

## Current scope

Authentication, one-time bootstrap, organization membership, tenant selection, tenant-scoped project CRUD, health checks, and initial security tests. Invitations, user administration, refresh tokens, password recovery, audit events, campaigns, and production deployment hardening remain subsequent tasks.
