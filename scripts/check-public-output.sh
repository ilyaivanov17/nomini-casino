#!/usr/bin/env sh
set -eu

OUT_DIR="${1:-public}"
if [ ! -d "$OUT_DIR" ]; then
  echo "ERROR: build output directory '$OUT_DIR' does not exist." >&2
  exit 1
fi
if [ ! -f "$OUT_DIR/index.html" ]; then
  echo "ERROR: '$OUT_DIR/index.html' is missing; this does not look like a built Hugo site." >&2
  exit 1
fi
for required in _headers _redirects; do
  if [ ! -f "$OUT_DIR/$required" ]; then
    echo "ERROR: '$OUT_DIR/$required' is missing. Check that static/$required exists." >&2
    exit 1
  fi
done

# Fail the deployment build if likely private/source artifacts leaked into the public output.
LEAKS=$(find "$OUT_DIR" \
  \( -type d -name '.git' -o -type f \( \
    -name '.env' -o -name '.env.*' -o -name '.DS_Store' -o -name '.htaccess' -o \
    -name '*.pem' -o -name '*.key' -o -name '*.p12' -o -name '*.pfx' -o \
    -name '*.toml' -o -name '*.sql' -o -name '*.dump' -o -name '*.zip' -o \
    -name '*.7z' -o -name '*.rar' -o -name '*.tar' -o -name '*.tar.gz' -o \
    -name '*.bak' -o -name '*.backup' -o -name '*.old' -o -name '*.map' \
  \) \) -print)
if [ -n "$LEAKS" ]; then
  echo "ERROR: possible private/source artifacts found in '$OUT_DIR':" >&2
  printf '%s\n' "$LEAKS" >&2
  exit 1
fi

# Protect source markdown and build configuration from accidental static copying.
LEAKS=$(find "$OUT_DIR" -type f \( -name '*.md' -o -name 'hugo.toml' -o -name 'wrangler.toml' -o -name 'wrangler.jsonc' \) -print)
if [ -n "$LEAKS" ]; then
  echo "ERROR: source documentation/configuration found in '$OUT_DIR':" >&2
  printf '%s\n' "$LEAKS" >&2
  exit 1
fi

echo "OK: '$OUT_DIR' contains a site index, Cloudflare Pages security files, and no checked source/secret artifacts."
