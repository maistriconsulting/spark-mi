# Deployment foundation

## Target topology

- Frontend: build React/Vite as static assets and publish `frontend/dist/` to the Hostinger document root for `sparkmi.maistriconsulting.com`.
- API public endpoint: `https://sparkmi-api.bianconiglio.eu`, routed through Cloudflare Tunnel.
- API service: run FastAPI on the Fedora server as the `spark-mi-api` systemd service, listening only on `127.0.0.1:8800`. The tunnel forwards requests to `http://127.0.0.1:8800`.
- Database: connect from Fedora to Hostinger MariaDB over TLS, after explicitly allowlisting the Fedora server's public egress IP in Hostinger.

The API hostname intentionally uses `bianconiglio.eu`: DNS for `maistriconsulting.com` is not hosted on Cloudflare, so it is not used as the Cloudflare Tunnel hostname. The frontend domain remains `sparkmi.maistriconsulting.com`.

## API and Cloudflare Tunnel

Configure the Cloudflare Tunnel public hostname:

- Hostname: `sparkmi-api.bianconiglio.eu`
- Service type: HTTP
- Origin service: `http://127.0.0.1:8800`

The API process must remain bound to loopback. Do not expose Uvicorn/FastAPI directly to the public internet and do not open inbound router ports for the API. Cloudflare Tunnel provides the public HTTPS endpoint and forwards traffic to the local service.

The API base URL is selected at frontend build time through `VITE_API_BASE_URL`; no application source-code change is required when changing this endpoint.

## Required network and security checks

1. Confirm the Cloudflare Tunnel is healthy and the public hostname `https://sparkmi-api.bianconiglio.eu` resolves and serves the API.
2. Confirm the tunnel origin points to `http://127.0.0.1:8800` on the Fedora server.
3. Confirm the `spark-mi-api` service remains bound to `127.0.0.1:8800`; do not expose port 8800 publicly.
4. Confirm Hostinger exposes remote MariaDB access for this database and identify the database hostname and port from hPanel.
5. Allowlist only the Fedora server's public egress IP in Hostinger. The source address observed by Hostinger during connectivity checks was `81.57.56.182`; verify that it is the server's stable egress address before relying on it for the allowlist.
6. Confirm outbound TCP access from Fedora to the MariaDB host on the configured port.
7. Confirm the database account is restricted to the required database and that TLS is enabled and verified.
8. Set `CORS_ORIGINS=https://sparkmi.maistriconsulting.com` on the backend.

Do not use `localhost` as the database host when the database is hosted by Hostinger and the API runs on Fedora. Do not allow remote database access from all IP addresses.

## Hostinger static frontend

Build on a development machine or CI runner with Node.js, setting the API URL to the Cloudflare Tunnel hostname:

```bash
cd frontend
npm install
VITE_API_BASE_URL=https://sparkmi-api.bianconiglio.eu/api/v1 npm run build
```

Upload the contents of `dist/`, including `.htaccess`, to the document root of `sparkmi.maistriconsulting.com`. Node.js is not needed on the Hostinger web server at runtime.

## Fedora API host

The API runs as the `spark-mi-api` systemd service and listens on `127.0.0.1:8800`. Keep the backend environment file outside version control and restrict its permissions to the service account. Store database credentials and signing/bootstrap secrets only in that protected environment or an appropriate secret manager; never commit them.

Run database migrations only after verifying application-level MariaDB authentication and TLS. Use a dedicated unprivileged Linux account, systemd, Cloudflare Tunnel, firewall rules, log rotation, and backups before production use.

## Current deployment notes

See [release status](release-status.md) for the deployed version and open items.
