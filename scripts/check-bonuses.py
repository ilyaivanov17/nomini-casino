#!/usr/bin/env python3
"""Validate the single-source bonus data file without asserting live validity."""
from pathlib import Path
import sys
try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML is required (python -m pip install PyYAML).")

path = Path("data/bonuses.yaml")
if not path.is_file():
    sys.exit("ERROR: data/bonuses.yaml is missing.")
items = yaml.safe_load(path.read_text(encoding="utf-8"))
if not isinstance(items, list) or len(items) != 3:
    sys.exit("ERROR: data/bonuses.yaml must contain exactly three offer records.")
seen = set()
for item in items:
    if not isinstance(item, dict):
        sys.exit("ERROR: each bonus must be a YAML mapping.")
    for key in ("code", "amount", "status", "source_url", "expires"):
        if key not in item:
            sys.exit(f"ERROR: bonus record missing '{key}'.")
    if not item["code"]:
        sys.exit("ERROR: each bonus needs a code.")
    if item["code"] in seen:
        sys.exit(f"ERROR: duplicate promo code '{item['code']}'.")
    seen.add(item["code"])
    if item["status"] == "verified" and not item["source_url"]:
        sys.exit(f"ERROR: verified bonus '{item['code']}' needs a source_url.")
print(f"OK: {len(items)} bonus records validated; verification status is not inferred.")
