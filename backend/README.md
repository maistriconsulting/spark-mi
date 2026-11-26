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

Use the activation script from an interactive terminal on the API host:

```bash
cd ~/apps/spark-mi/backend
.venv/bin/python scripts/activate_superadmin.py
```

It asks for the password, creates the account, verifies login and `GET /api/v1/auth/platform/overview`, checks that a repeated bootstrap returns 409 while the token is still configured, then blanks `BOOTSTRAP_TOKEN`, restarts the service and checks that the endpoint now returns 404. It can be re-run if it stops halfway.

The frontend has no bootstrap form.

## Authentication and tenant access

Login returns a user token. `GET /api/v1/auth/tenants` lists organizations for which the user has an active membership. `POST /api/v1/auth/select-tenant` issues a tenant-scoped token after checking that membership.

The global superadmin role is stored on the user record and checked server-side. It is separate from tenant membership and does not bypass tenant context or grant automatic access to tenant data. Tenant-scoped APIs continue to require a valid active membership and verified tenant context.

`GET /api/v1/auth/platform/overview` is restricted to the database-backed global superadmin role and returns the platform overview and active organization list. Management operations are described below.

## Platform management (superadmin only)

All routes live under `/api/v1/platform` and check the database-backed superadmin flag:

| Route | Purpose |
|---|---|
| `GET /roles` | The five fixed organization roles and what the API enforces today |
| `GET`, `POST /tenants`; `PATCH /tenants/{id}` | List, create, rename, suspend and reactivate organizations |
| `GET`, `POST /users`; `PATCH /users/{id}` | List, create, rename, deactivate and reactivate users |
| `POST /users/{id}/reset-password` | Generate a new temporary password, returned once |
| `PUT /tenants/{id}/members/{user_id}` | Add a member, change role, revoke or restore access |
| `GET /audit` | Administrative audit log |

Rules: nothing is hard-deleted; the superadmin flag cannot be set through the API; superadmin accounts cannot be deactivated or reset here; the last active owner of an organization cannot be demoted or revoked (deactivating that user is still allowed, and the UI then flags the organization as having no owner). Suspending an organization blocks tenant access on the next request. Every change writes an `audit_events` row without secrets.

There is no email flow yet: new users receive a generated temporary password that the administrator delivers manually. Users change it with `POST /api/v1/auth/change-password`. A password change or reset does not revoke tokens already issued (they expire within `ACCESS_TOKEN_EXPIRE_MINUTES`); deactivation takes effect immediately.

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

Authentication, one-time global superadmin bootstrap, tenant membership and selection, tenant-scoped project listing and creation, health checks, platform management of organizations, users and roles, and the administrative audit log.

Invitations, delegated administration by tenant owners and admins, refresh tokens, password recovery, login rate limiting, campaigns and further production hardening are not implemented.
