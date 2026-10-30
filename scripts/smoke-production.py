#!/usr/bin/env python3
"""Small post-deploy HTTP smoke test for the public Cloudflare Pages site."""
from __future__ import annotations
import sys
import urllib.error
import urllib.request
from urllib.parse import urljoin

PATHS = ["/", "/de/", "/es/", "/pt/", "/pl/", "/ja/", "/go/"]

def fetch(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "InstantCasino-ProductionSmoke/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.status, response.headers, response.read(500_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers, exc.read(500_000).decode("utf-8", "replace")

if len(sys.argv) != 2:
    sys.exit("Usage: python3 scripts/smoke-production.py https://example.com")
base = sys.argv[1].rstrip("/") + "/"
failed = False
for path in PATHS:
    url = urljoin(base, path.lstrip("/"))
    status, headers, body = fetch(url)
    ok = status == 200 and "<html" in body.lower()
    print(f"{'OK' if ok else 'FAIL'} {status} {url}")
    if not ok:
        failed = True
    if path == "/go/":
        robots = headers.get("X-Robots-Tag", "").lower()
        if "noindex" not in robots:
            print(f"FAIL missing X-Robots-Tag noindex on {url}")
            failed = True
        else:
            print(f"OK X-Robots-Tag: {robots}")
if failed:
    sys.exit(1)
print("Production smoke test passed.")
