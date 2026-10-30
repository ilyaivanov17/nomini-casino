#!/usr/bin/env python3
"""Create linked, non-publishable content drafts for all configured site languages."""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

LANGUAGES = {
    "de": ("Entwurf: Titel ergänzen", "Entwurf: Beschreibung ergänzen"),
    "en": ("Draft: add title", "Draft: add description"),
    "es": ("Borrador: añadir título", "Borrador: añadir descripción"),
    "pt": ("Rascunho: adicionar título", "Rascunho: adicionar descrição"),
    "pl": ("Szkic: dodaj tytuł", "Szkic: dodaj opis"),
    "ja": ("下書き：タイトルを追加", "下書き：説明を追加"),
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("slug", help="URL-safe slug, e.g. bonus-terms-checklist")
parser.add_argument("--type", default="page", choices=("page", "article", "bonus", "payment", "slot", "faq"))
args = parser.parse_args()
slug = args.slug.strip().lower()
if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
    sys.exit("ERROR: slug must contain lowercase ASCII letters, numbers and single hyphens only.")

created = []
for lang, (title, description) in LANGUAGES.items():
    path = Path("drafts") / lang / f"{slug}.md"
    if path.exists():
        sys.exit(f"ERROR: refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    body = f'''---\ntitle: "{title}"\ndescription: "{description}"\ntype: "{args.type}"\nseo_title: "TODO: add localized SEO title"\nslug: "{slug}"\ndraft: true\narticle_review_status: "draft"\ntranslationKey: "{slug}"\nlastmod: ""\nsource_urls: []\nreviewed_by: ""\nreviewed_at: ""\n---\n\n<!-- TODO: Write and fact-check this language version. Do not publish untranslated placeholders. -->\n\n## TODO: Add a useful, source-backed introduction\n\nTODO: Add original language-specific content, relevant examples, and links to primary sources.\n\n## TODO: Add practical details\n\nTODO: Explain the topic clearly; mark unknown information as unknown instead of inventing it.\n\n## Editorial checklist\n\n- [ ] Verify factual claims against primary sources.\n- [ ] Adapt the content for the target language and market.\n- [ ] Check internal links, title, description and canonical URL.\n- [ ] Complete editorial and legal review where relevant.\n'''
    path.write_text(body, encoding="utf-8")
    created.append(str(path))
print("Created isolated draft files (not included in Hugo production builds):")
print("\n".join(f"  - {p}" for p in created))
print("Next: edit every language version, then promote only after all six are reviewed.")
