#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

printf '\n== Instant Casino: full project check ==\n'
for tool in python3 hugo; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "ERROR: required command not found: $tool" >&2
    exit 127
  fi
done

python3 scripts/check-site.py
python3 scripts/check-bonuses.py
python3 scripts/seo-audit.py
python3 scripts/language-coverage.py
python3 scripts/check-locales.py

# Build into the same public/ directory Cloudflare Pages publishes.
hugo --cleanDestinationDir --minify --environment production --printPathWarnings
python3 scripts/check-sitemap.py
./scripts/check-public-output.sh public
printf '\nOK: all checks passed and the production output is ready in ./public/\n'
