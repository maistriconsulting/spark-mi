# Hostinger SSH frontend deployment

The workflow `.github/workflows/deploy-hostinger.yml` builds the Vite app and synchronizes only `frontend/dist/` to the Hostinger document root. It does not deploy the backend or repository source.

## One-time Hostinger preparation

1. In hPanel, keep the GitHub repository connected but change its native deployment from automatic to manual/off. Do not disconnect the repository. The native deployment copies repository contents and would conflict with this workflow.
2. Enable SSH access in Hostinger and note the SSH hostname, port and username.
3. Generate a dedicated Ed25519 key pair on a trusted local computer:
   ```bash
   ssh-keygen -t ed25519 -C "github-actions-spark-mi-hostinger" -f spark-mi-hostinger
   ```
4. Add the contents of `spark-mi-hostinger.pub` to the SSH authorized keys in Hostinger. Never upload or share the private key file except by storing its contents in the GitHub Actions secret described below.
5. Connect once from the trusted local computer and verify the server host-key fingerprint against Hostinger's official information/support. Only after verification, capture the matching known_hosts line for the configured host and port (for a non-standard port, use `ssh-keyscan -p PORT HOST` and independently verify its fingerprint).
6. Use SSH to identify the exact absolute document-root path for `sparkmi.maistriconsulting.com`. It must end in `/public_html`. Do not guess this path.

## GitHub Actions secrets

In GitHub, open Settings > Secrets and variables > Actions > New repository secret. Add:

| Secret | Value |
|---|---|
| `HOSTINGER_SSH_HOST` | SSH hostname supplied by Hostinger |
| `HOSTINGER_SSH_PORT` | SSH port supplied by Hostinger |
| `HOSTINGER_SSH_USER` | SSH username supplied by Hostinger |
| `HOSTINGER_SSH_PRIVATE_KEY` | Full contents of the private `spark-mi-hostinger` key |
| `HOSTINGER_SSH_KNOWN_HOSTS` | Verified known_hosts line for this host and port |
| `HOSTINGER_SSH_TARGET` | Exact absolute document-root path ending in `/public_html` |

Do not put credentials in repository files, workflow YAML, chat messages or screenshots.

## Enable the workflow

After the pull request is merged into `feat/multi-tenant-foundation`, open Settings > Secrets and variables > Actions > Variables and create:

- Name: `HOSTINGER_DEPLOY_ENABLED`
- Value: `true`

The workflow then runs on pushes affecting `frontend/**` or the deployment workflow itself, and can also be started manually from Actions.

The build sets `VITE_API_BASE_URL=https://sparkmi-api.bianconiglio.eu/api/v1`, runs `npm run build`, verifies `dist/index.html`, copies `.htaccess` into `dist/`, and deploys only that directory.

The rsync command uses `--delete` inside the configured target directory. Confirm the target path carefully: it must be the dedicated document root for `sparkmi.maistriconsulting.com`, not a parent directory or another site's root.

## First deployment verification

After a successful run, confirm that `index.html`, `.htaccess` and `assets/` are directly inside the domain's `public_html`. Then test the site, browser refresh on a nested route, login and the API connection.
