#!/usr/bin/env bash
set -euo pipefail

# Avoid noisy LiveReload WebSocket failures in forwarded IDE environments.
exec hugo server --disableLiveReload --bind 0.0.0.0 --port "${PORT:-1313}"
