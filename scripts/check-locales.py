#!/usr/bin/env python3
"""Check that public-facing source files contain no Cyrillic characters."""
from pathlib import Path
import sys
ROOTS = (Path("content"), Path("layouts"), Path("i18n"), Path("data"), Path("static"))
EXTS = {".md", ".html", ".toml", ".yaml", ".yml", ".json", ".xml", ".txt", ".js", ".css", ".svg"}
issues = []
for root in ROOTS:
    if not root.exists():
        continue
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTS:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            issues.append(f"{path}: not valid UTF-8")
            continue
        for number, line in enumerate(lines, 1):
            chars = sorted({c for c in line if "\u0400" <= c <= "\u052f"})
            if chars:
                issues.append(f"{path}:{number}: Cyrillic characters found ({''.join(chars)})")
if issues:
    print("ERROR: Cyrillic text detected in public-facing source files:", file=sys.stderr)
    print("\n".join(issues), file=sys.stderr)
    sys.exit(1)
print("OK: no Cyrillic characters found in public-facing source files.")
