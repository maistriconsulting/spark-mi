# Deployment foundation

## Target topology

- Frontend: build React/Vite as static assets and publish `frontend/dist/` to the Hostinger document root for `sparkmi.maistriconsulting.com`.
- API: run FastAPI on the Fedora server at `api.sparkmi.maistriconsulting.com`, behind a reverse proxy with HTTPS. Do not expose Uvicorn directly to the public internet.
- Database: connect from Fedora to Hostinger MariaDB over TLS, after explicitly allowlisting the Fedora server's fixed public egress IP in Hostinger.

## Required network checks

1. Create an A record for `api.sparkmi.maistriconsulting.com` pointing to the Fedora server's public IP.
2. Configure HTTPS for the API hostname using a reverse proxy on Fedora.
3. Confirm Hostinger exposes remote MariaDB access for this database and identify the database hostname and port from hPanel.
4. Add only the Fedora server's public egress IP to the Hostinger remote database allowlist.
5. Confirm outbound TCP access from Fedora to the MariaDB host on the configured port.
6. Confirm the database account is restricted to the required database and TLS is available.
7. Set `CORS_ORIGINS=https://sparkmi.maistriconsulting.com` on the backend.

Do not use `localhost` as the database host when the database is hosted by Hostinger and the API runs on Fedora. Do not allow remote database access from all IP addresses.

## Hostinger static frontend

Build on a development machine or CI runner with Node.js:

```bash
cd frontend
npm install
VITE_API_BASE_URL=https://api.sparkmi.maistriconsulting.com/api/v1 npm run build
```

Upload the contents of `dist/`, including `.htaccess`, to the document root of `sparkmi.maistriconsulting.com`. Node.js is not needed on the Hostinger web server at runtime.

## Fedora API host

Copy the root `.env.example` to `backend/.env` or inject the variables through the service manager. Keep the file outside version control and restrict its permissions to the service account. Run migrations before starting the service. Use a dedicated unprivileged Linux account, systemd, a reverse proxy, HTTPS, firewall rules, log rotation, and backups before production use.

This document describes the intended deployment topology. It does not claim that connectivity, DNS, reverse proxying, or deployment have already been configured.
