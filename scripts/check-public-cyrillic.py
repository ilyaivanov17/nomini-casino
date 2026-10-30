#!/usr/bin/env python3
"""Fail when generated public text contains Cyrillic characters."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TEXT_EXTENSIONS = {".html", ".xml", ".txt", ".json", ".js", ".css", ".svg", ".webmanifest"}
CYRILLIC = re.compile(r"[\u0400-\u04FF\u0500-\u052F]")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", type=Path, default=Path("public"))
    root = parser.parse_args().directory

    if not root.is_dir():
        print(f"ERROR: public output directory does not exist: {root}", file=sys.stderr)
        return 2

    checked = 0
    failures: list[tuple[str, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Binary or non-UTF-8 assets are outside this textual-content check.
            continue
        checked += 1
        match = CYRILLIC.search(text)
        if match:
            start = max(0, match.start() - 24)
            end = min(len(text), match.end() + 24)
            snippet = text[start:end].replace("\n", " ")
            failures.append((str(path), snippet))

    if failures:
        print("ERROR: Cyrillic characters found in generated public text:")
        for name, snippet in failures:
            print(f" - {name}: {snippet}")
        return 1

    print(f"PASS: checked {checked} generated text files; no Cyrillic characters found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
