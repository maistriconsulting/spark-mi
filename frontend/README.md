# SPARK-MI frontend

React + TypeScript + Vite static frontend, deployable on Hostinger PHP Web Hosting without Node.js at runtime.

## Build locally

```bash
npm install
npm run build
```

Upload the contents of `dist/` to the document root for `sparkmi.maistriconsulting.com`. The `.htaccess` file enables client-side route fallback and basic response headers.

Set `VITE_API_BASE_URL` at build time. For same-origin reverse proxy routing, use `/api/v1`. If the API is hosted on a separate hostname, use its HTTPS API base URL and add that exact origin to the backend CORS allowlist.

Node.js is required only on the development/build machine or CI runner, not on Hostinger for serving the compiled static assets.
