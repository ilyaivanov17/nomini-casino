#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
command -v hugo >/dev/null || { echo 'ERROR: Hugo is required.' >&2; exit 127; }
node -e "require('playwright')" >/dev/null 2>&1 || { echo 'ERROR: install Playwright first: npm install --no-save playwright && npx playwright install chromium' >&2; exit 127; }
hugo --cleanDestinationDir --minify --environment production
python3 -m http.server 4173 --directory public >/tmp/instant-casino-preview.log 2>&1 &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true' EXIT
for _ in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:4173/ >/dev/null; then break; fi
  sleep 1
done
node tests/mobile-smoke.cjs
