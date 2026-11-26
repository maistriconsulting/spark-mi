# SPARK-MI frontend

React + TypeScript + Vite static frontend, deployable on Hostinger PHP Web Hosting without Node.js at runtime.

## Build locally

```bash
npm install
VITE_API_BASE_URL=https://api.sparkmi.maistriconsulting.com/api/v1 npm run build
```

Upload the contents of `dist/` to the document root for `sparkmi.maistriconsulting.com`. The `.htaccess` file enables client-side route fallback and basic response headers.

The API is intended to run on the Fedora server at `api.sparkmi.maistriconsulting.com`, behind an HTTPS reverse proxy. Set that URL in `VITE_API_BASE_URL` at build time and configure backend `CORS_ORIGINS=https://sparkmi.maistriconsulting.com`.

Node.js is required only on the development/build machine or CI runner, not on Hostinger for serving the compiled static assets.
