# Instant Casino — Quick Start

This project uses Hugo and deploys as a static site on Cloudflare Pages.

## Requirements

- Hugo **Extended** (use the same major version locally and in CI)
- Python 3.10+
- Python package `PyYAML` for content audits

## Daily workflow

```bash
make dev       # local preview at http://localhost:1313
make check     # all audits + production build + public-file safety check
make build     # production build + public-file safety check
make clean     # remove generated files
make draft SLUG=my-new-page TYPE=article  # create six isolated language drafts
make promote SLUG=my-new-page REVIEWER=editor  # validate and promote reviewed drafts
```

Equivalent commands are available in `scripts/` if you prefer not to use Make.

## Cloudflare Pages settings

- Build command: `./scripts/build-production.sh`
- Build output directory: `public`
- Production branch: `main`

For the full pre-deploy gate, use `./scripts/check-all.sh` in CI. Keep the repository private and never commit real secrets. Only files inside `public/` are meant to be deployed.

## Content rules

- Site languages: German, English, Polish, Spanish, Portuguese and Japanese.
- Do not add Russian/Cyrillic copy to user-facing content.
- `/go/` is a tracking/redirect path and should remain `noindex`.
- Verify bonus amounts and terms against the operator's current official terms before publishing; do not present unverified offers as guaranteed.

## Troubleshooting

- `hugo: command not found`: install Hugo Extended.
- Missing PyYAML: run `python3 -m pip install PyYAML` in your local environment.
- If the local preview is exposed through an IDE port-forward, `--disableLiveReload` avoids noisy websocket reconnects.

## Simplified workflow

From the repository root:

- `make dev` — start the local Hugo preview.
- `make check` — run content, SEO, locale coverage, bonus-data and production-output checks. Requires Hugo Extended and Python 3; install `PyYAML` for the YAML data check.
- `make build` — create and validate the production output in `public/`.
- `make mobile-check` — run Chromium mobile smoke tests. Install dependencies first with `npm install --no-save playwright && npx playwright install chromium`.
- `make smoke URL=https://your-live-domain.example` — check the deployed home page, language routes, bonus page and `/go/` noindex header over HTTP.
- `make clean` — remove generated output and Hugo cache.

## Central bonus data

Edit `data/bonuses.yaml` to update the displayed bonus amount and code. The three records are shown in the promo-code component across languages. They follow the order provided by the site owner, but are deliberately marked `owner_supplied_unverified`; add a primary-source URL and expiry, and only mark a record `verified` after checking official terms. Do not treat this status field as a guarantee that the promotion is active.

## Release checklist

1. Run `make check` and resolve every error.
2. Run `make mobile-check` to catch JavaScript errors and horizontal overflow at a 390px viewport.
3. Preview the Cloudflare Pages deployment and manually inspect key pages on desktop and mobile.
4. After publishing, run `make smoke URL=https://your-live-domain.example`.
5. Keep API keys and private configuration out of the public Hugo output; set secrets in Cloudflare project settings instead.

## Draft-first content workflow

See `CONTENT-FACTORY.md` and `MODERNIZATION-PLAN.md`. New page scaffolds live under `drafts/` and are not built by Hugo. Edit all six language versions, remove every TODO, and only then run `make promote SLUG=... REVIEWER=...`. Promotion records the human reviewer but does not replace fact-checking, legal review, CI, or manual Cloudflare Preview approval.
