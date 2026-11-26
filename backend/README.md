# SPARK-MI API

FastAPI backend for the SPARK-MI multi-tenant platform.

## Local setup

1. Create a virtual environment and install dependencies:

   `python -m venv .venv && source .venv/bin/activate`
   `pip install -r requirements.txt`

2. Copy the root `.env.example` to `.env` and set the database connection and secrets.
3. Create and apply the initial migration:

   `alembic revision --autogenerate -m "initial tenant foundation"`
   `alembic upgrade head`

4. Run the API:

   `uvicorn app.main:app --host 127.0.0.1 --port 8000`

## First setup

Call `POST /api/v1/auth/bootstrap` once with the bootstrap token, first owner credentials, and initial organization. The endpoint is disabled after the first user or tenant exists. Remove `BOOTSTRAP_TOKEN` from the environment after successful initialization.

Login returns a user token. Call `GET /api/v1/auth/tenants`, then `POST /api/v1/auth/select-tenant` to receive a tenant-scoped token. Tenant access is revalidated against active membership on every request.

## Hostinger MariaDB

The Fedora host must be explicitly allowed by Hostinger's remote database access controls. Prefer TLS, a dedicated least-privilege database user, a strong password, and a firewall allowlist restricted to the Fedora server's public IP. Never expose MariaDB to all IP addresses. Verify Hostinger's supported TLS settings before production use.

## Current scope

Authentication, one-time bootstrap, organization membership, tenant selection, tenant-scoped project CRUD, health checks, and initial security tests. Campaigns, invitations, refresh tokens, password recovery, audit events, and production deployment hardening remain subsequent tasks.
