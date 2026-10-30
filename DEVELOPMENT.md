## Quick commands

Use `make help` to see the short command list. The main workflow is:

- `make dev` — local Hugo preview.
- `make check` — content, SEO, translation, production build and public-output checks.
- `make build` — production build and public-output safety checks.
- `make clean` — remove generated output.

Cloudflare Pages should publish only `public/`. Keep `productionReady = false` until the operator/contact details and offer sources have been independently verified; the automated audit will block a misleading production-ready status.

# Development and production commands

## Local preview in a forwarded environment

Hugo injects its LiveReload client when `hugo server` is running. If the forwarded environment does not support the LiveReload WebSocket, start the preview without that client:

```bash
./scripts/dev-preview.sh
```

Or run the equivalent command directly:

```bash
hugo server --disableLiveReload --bind 0.0.0.0 --port 1313
```

The browser message about deferred lazy-image load events is a Chromium performance notice. It is not a missing-image or JavaScript failure. Keep below-the-fold content lazy-loaded; the homepage hero image is explicitly high priority.

## Production build

Do not deploy the `public-archive-previous-build` directory. It is a historical snapshot, not the current build output. Generate a clean static site from the current Hugo source:

```bash
hugo --cleanDestinationDir --minify --environment production --printPathWarnings
./scripts/check-public-output.sh
```

Hugo writes the current site to `public/`. The production build does not inject the development LiveReload client.

## After changing styles

The main stylesheet uses a versioned query parameter to avoid reusing a stale browser cache. Hard-refresh the browser once after updating the project.

## Cloudflare Pages production hardening

Cloudflare Pages response headers, noindex rules for `/go/` and Pages hostnames, defense-in-depth source-path redirects, and a public-output leak check are configured in `static/_headers`, `static/_redirects`, and `scripts/check-public-output.sh`. Review `deploy/CLOUDFLARE-PAGES-SECURITY.md` for required Cloudflare dashboard settings and post-deploy verification.
