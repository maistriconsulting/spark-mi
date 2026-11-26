# SPARK-MI frontend

React + TypeScript + Vite static frontend, deployable on Hostinger PHP Web Hosting without Node.js at runtime.

## Look and feel

`src/tokens.css` and `public/brand/` are copies of Spark CRM's design tokens and logo. As in Spark, colour literals belong only in `tokens.css` (the `theme-color` meta tag in `index.html` is the one exception), styles are mobile first and the breakpoints are 640px and 1024px.

## Build locally

```bash
npm install
VITE_API_BASE_URL=https://sparkmi-api.bianconiglio.eu/api/v1 npm run build
```

Upload the contents of `dist/` to the document root for `sparkmi.maistriconsulting.com`. The `public/.htaccess` file (copied into `dist/` by the build) enables client-side route fallback and basic response headers.

The API runs on the Fedora server behind the configured HTTPS tunnel/reverse proxy. Set `VITE_API_BASE_URL=https://sparkmi-api.bianconiglio.eu/api/v1` at build time and configure backend `CORS_ORIGINS=https://sparkmi.maistriconsulting.com`.

Node.js is required only on the development/build machine or CI runner, not on Hostinger for serving the compiled static assets. Publish the updated frontend only after the matching backend release is available, because the UI depends on its authentication endpoints. The first superadmin account is not created from the browser: see `backend/README.md`.
