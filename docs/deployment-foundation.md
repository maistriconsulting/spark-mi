# Deployment foundation

## Target topology

- Frontend: build React/Vite as static assets and publish `frontend/dist/` to the Hostinger document root for `sparkmi.maistriconsulting.com`.
- API: run FastAPI on the Fedora server, behind a reverse proxy with HTTPS. Do not expose Uvicorn directly to the public internet.
- Database: connect from Fedora to Hostinger MariaDB over TLS, after explicitly allowlisting the Fedora server's fixed public egress IP in Hostinger.

## Required network checks

1. Confirm Hostinger exposes remote MariaDB access for this database and identify the database hostname and port from hPanel.
2. Add only the Fedora server's public egress IP to the Hostinger remote database allowlist.
3. Confirm outbound TCP access from Fedora to the MariaDB host on the configured port.
4. Confirm the database account is restricted to the required database and TLS is available.
5. Configure the API hostname or reverse proxy route and set `CORS_ORIGINS` to the exact frontend origin.

Do not use `localhost` as the database host when the database is hosted by Hostinger and the API runs on Fedora. Do not allow remote database access from all IP addresses.

## Hostinger static frontend

Build on a development machine or CI runner with Node.js:

```bash
cd frontend
npm install
npm run build
```

Upload the contents of `dist/`, including `.htaccess`, to the document root of `sparkmi.maistriconsulting.com`. Node.js is not needed on the Hostinger web server at runtime.

The frontend currently expects the API at `/api/v1`. This requires a same-origin reverse proxy from the Hostinger site to the Fedora API. If that proxy is unavailable, build with `VITE_API_BASE_URL` set to the separate HTTPS API URL and configure backend CORS accordingly.

## Fedora API host

Copy the root `.env.example` to `backend/.env` or inject the variables through the service manager. Keep the file outside version control and restrict its permissions to the service account. Run migrations before starting the service. Use a dedicated unprivileged Linux account, systemd, a reverse proxy, HTTPS, firewall rules, log rotation, and backups before production use.

This document describes the intended deployment topology. It does not claim that connectivity, DNS, reverse proxying, or deployment have already been configured.
