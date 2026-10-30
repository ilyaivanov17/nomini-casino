#!/usr/bin/env python3
"""Promote a fully edited six-language draft into Hugo content after human review."""
from __future__ import annotations
import argparse
from datetime import date
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML is required (python -m pip install PyYAML).")

LANGS = ("de", "en", "es", "pt", "pl", "ja")
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("slug", help="Draft slug created with make draft")
parser.add_argument("--reviewed-by", required=True, help="Name or editorial handle of the human reviewer")
args = parser.parse_args()
slug = args.slug.strip().lower()
reviewer = args.reviewed_by.strip()
if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
    sys.exit("ERROR: invalid slug.")
if not reviewer:
    sys.exit("ERROR: --reviewed-by cannot be empty.")

records = []
for lang in LANGS:
    src = Path("drafts") / lang / f"{slug}.md"
    dst = Path("content") / lang / f"{slug}.md"
    if not src.is_file():
        sys.exit(f"ERROR: missing draft: {src}")
    if dst.exists():
        sys.exit(f"ERROR: refusing to overwrite existing content: {dst}")
    raw = src.read_text(encoding="utf-8")
    if not raw.startswith("---\n") or "\n---\n" not in raw[4:]:
        sys.exit(f"ERROR: invalid YAML front matter: {src}")
    _, rest = raw.split("---\n", 1)
    front, body = rest.split("\n---\n", 1)
    metadata = yaml.safe_load(front)
    if not isinstance(metadata, dict):
        sys.exit(f"ERROR: invalid metadata: {src}")
    for field in ("title", "description", "seo_title"):
        value = str(metadata.get(field, "")).strip()
        if not value or "TODO" in value.upper() or value.lower().startswith(("draft:", "entwurf:", "borrador:", "rascunho:", "szkic:", "下書き")):
            sys.exit(f"ERROR: {src} needs a real localized '{field}'.")
    if "TODO" in body.upper():
        sys.exit(f"ERROR: unresolved TODO placeholder in {src}")
    metadata["draft"] = False
    metadata["article_review_status"] = "reviewed"
    metadata["reviewed_by"] = reviewer
    metadata["reviewed_at"] = date.today().isoformat()
    metadata["lastmod"] = date.today().isoformat()
    records.append((src, dst, metadata, body.lstrip("\n")))

# Validate all six first; only then write any production content.
for src, dst, metadata, body in records:
    dst.parent.mkdir(parents=True, exist_ok=True)
    rendered = "---\n" + yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, default_flow_style=False).rstrip() + "\n---\n\n" + body
    dst.write_text(rendered, encoding="utf-8")
print(f"Promoted {len(records)} localized pages for '{slug}'.")
print("Human approval is recorded in front matter; still run make check and inspect the Cloudflare Preview before merging.")
