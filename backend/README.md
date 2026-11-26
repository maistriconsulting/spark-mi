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

Configure the database connection and generated secrets in the local environment file. Never commit real credentials or tokens.

Apply the migrations and start the API locally:

```bash
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## First setup — global superadmin

The one-time endpoint `POST /api/v1/auth/bootstrap` creates only the global superadmin user with the fixed email `info@maistriconsulting.com`. It does **not** create an organization (tenant) or a membership. The password is chosen at activation time and is not stored in this repository.

The request requires the `X-Bootstrap-Token` header. Run it only from a trusted operator context on the server. Do not put the token in browser JavaScript, frontend configuration, source control, logs, or shell command history. The password must be entered interactively by the operator and must be at least 12 characters long.

The bootstrap endpoint is available only while the bootstrap token is configured and no user or tenant exists. A missing or incorrect token returns 404. If an account or tenant already exists, bootstrap returns 409. `GET /api/v1/auth/bootstrap-status` reports whether initialization has already occurred.

After successful initialization:

1. Verify login for `info@maistriconsulting.com`.
2. Verify `GET /api/v1/auth/platform/overview` with the superadmin token.
3. Remove `BOOTSTRAP_TOKEN` from the protected service environment.
4. Restart the backend and verify that a repeated bootstrap attempt returns 409.

Do not expose the bootstrap token through the frontend. The initial setup UI must not be used to send the token from the browser.

## Authentication and tenant access

Login returns a user token. `GET /api/v1/auth/tenants` lists organizations for which the user has an active membership. `POST /api/v1/auth/select-tenant` issues a tenant-scoped token after checking that membership.

The global superadmin role is stored on the user record and checked server-side. It is separate from tenant membership and does not bypass tenant context or grant automatic access to tenant data. Tenant-scoped APIs continue to require a valid active membership and verified tenant context.

`GET /api/v1/auth/platform/overview` is restricted to the database-backed global superadmin role and returns the platform overview and active organization list. Organization editing and management operations are outside the first-release scope.

## Production topology

The production API runs on the Fedora host, bound to loopback and exposed through the configured HTTPS tunnel/reverse proxy. The frontend is a static React/Vite build hosted on Hostinger.

Current frontend API base URL:

```text
https://sparkmi-api.bianconiglio.eu/api/v1
```

The backend CORS configuration must allow the frontend origin:

```text
https://sparkmi.maistriconsulting.com
```

The Fedora host must be explicitly allowed by Hostinger's remote database access controls. Prefer TLS, a dedicated least-privilege database user, a strong password, and a firewall allowlist restricted to the Fedora server's public IP. Never expose MariaDB to all IP addresses.

## Current first-release scope

Authentication, one-time global superadmin bootstrap, tenant membership and selection, tenant-scoped project CRUD, health checks, and the initial platform overview.

Invitations, user administration, refresh tokens, password recovery, audit events, campaigns, superadmin organization editing, and further production hardening are outside this release batch.
