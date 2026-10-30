# Instant Casino — Cloudflare Pages production security

This project is a static Hugo site. Browser-delivered HTML, CSS, JavaScript, and images are public by design; do not put secrets in them. This configuration hardens browser response headers, marks `/go/` as noindex, prevents the Pages project hostnames from being indexed, blocks common accidental source-file URLs, and provides a pre-deploy artifact check. It is not encryption and does not make the public site source invisible.

## Cloudflare Pages build settings

- Framework preset: Hugo (or Custom).
- Build command: `hugo --cleanDestinationDir --minify --environment production && ./scripts/check-public-output.sh`
- Build output directory: `public`
- Root directory: repository root (empty unless the project is nested).
- Production branch: `main` (or the actual release branch used by the repository).

`static/_headers` and `static/_redirects` are copied by Hugo to `public/` and interpreted by Cloudflare Pages. Do not configure the build output directory as the repository root. Do not deploy `public-archive-previous-build/`; it is an old archived snapshot.

## Cloudflare dashboard checklist

1. In Workers & Pages → the Instant Casino project → Settings → Builds & deployments, confirm the build command and output directory above.
2. In Settings → General, enable the access policy for preview deployments so branch/PR preview URLs require authentication. Cloudflare documents that preview URLs are public by default; this setting does not automatically protect the stable `<project>.pages.dev` hostname.
3. If the stable `<project>.pages.dev` hostname should not be public, separately configure Cloudflare Access for that hostname using the current Cloudflare Pages known-issues guide. Keep the production custom domain public. Do not accidentally apply the Access policy to `instant.slot-reviews.com`.
4. In SSL/TLS, use Full (strict) and ensure HTTPS is active for the custom domain before relying on HSTS.
5. Store any future API keys, tokens, or credentials in Cloudflare environment variables/secrets or the relevant server-side secret store. Never put them in `static/`, page front matter, `hugo.toml`, client-side JS, or public Git history.
6. Keep the Git repository private; require MFA, protect the production branch, and review commits for secrets. `.gitignore` is only a convenience and does not remove secrets already committed. If a secret has ever been committed, revoke/rotate it and clean repository history as appropriate.
7. After deployment, test headers and protected paths (commands below). The `_redirects` rules are defense in depth, not a substitute for keeping private files out of the build output.

## Verification

Build locally before release:

```sh
hugo --cleanDestinationDir --minify --environment production
./scripts/check-public-output.sh
```

After deployment, run these checks against the real production domain:

```sh
curl -sSI https://instant.slot-reviews.com/
curl -sSI https://instant.slot-reviews.com/go/
curl -sSI https://instant.slot-reviews.com/.env
curl -sSI https://instant.slot-reviews.com/hugo.toml
```

Expected: the home page has the security headers; `/go/` has `X-Robots-Tag: noindex, nofollow`; `.env` and `hugo.toml` return 404. If the root `/go/` URL is not an actual page and redirects before headers are applied, also test a known `/go/...` endpoint. Verify the current production and preview hostnames independently.

## Header policy notes

- This baseline deliberately does not set a Content-Security-Policy yet. CSP can block inline styles, scripts, images, and third-party integrations if not matched to the actual page. Add and test a tailored CSP after a browser-console audit; do not paste a generic CSP blindly.
- HSTS is set for the host only (without `includeSubDomains` or `preload`) to avoid unintentionally forcing unrelated subdomains to HTTPS.
- `/go/` remains blocked from indexing through both page metadata/robots policy already in the project and the response header here. `robots.txt` alone is not a reliable way to keep a URL out of an index.
