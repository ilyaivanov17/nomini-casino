#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import glob
import os
import re
import sys
import ast
from collections import defaultdict
import tomllib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LANGS = ("de", "en", "pl", "es", "pt", "ja")
REQUIRED_FRONT_MATTER = {"title", "description", "seo_title", "type"}

HARDCODED_TEMPLATE_MARKERS = (
    'aria-label="Primary navigation"',
    '<label class="sr-only" for="language-select">Language</label>',
    'aria-label="Breadcrumb"',
    'Ready to play?',
    'Prêt à jouer ?',
    '¿Listo para jugar?',
    'Erwachsene',
    'Adultes',
    'Adultos',
)

def read_front_matter(path):
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---"):
        raise ValueError(f"{path}: missing YAML front matter")
    parts = text.split("---", 2)
    data = {}
    parent = None
    for line in parts[1].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            key, separator, value = line.partition(":")
            if not separator:
                continue
            parent = key.strip()
            value = value.strip()
            data[parent] = yaml_scalar(value) if value else {}
        elif parent in {"ui", "sitemap", "build"}:
            key, separator, value = line.strip().partition(":")
            if separator:
                data[parent][key.strip()] = yaml_scalar(value.strip())
    body = parts[2]
    return data, body

def yaml_scalar(value):
    if not value:
        return ""
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "~"}:
        return None
    if value.startswith('"') and value.endswith('"'):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value

def load_yaml(path):
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyYAML is required to validate release-only YAML registers") from exc
    with open(path, encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}

def page_key(filename, content_root):
    relative = os.path.relpath(filename, content_root).replace(os.sep, "/")
    parts = relative.split("/")
    if len(parts) > 1 and parts[0] in LANGS:
        lang = parts[0]
        stem = "/".join(parts[1:])
        return stem[:-3] if stem.endswith(".md") else stem, lang
    stem = relative[:-3] if relative.endswith(".md") else relative
    return stem, "de"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=ROOT)
    args = parser.parse_args()
    root = os.path.abspath(args.root)

    errors = []
    warnings = []

    with open(os.path.join(root, "hugo.toml"), "rb") as f:
        cfg = tomllib.load(f)

    settings = {}
    for lang in LANGS:
        suffix = "" if lang == "de" else f".{lang}"
        settings_path = os.path.join(root, "content", lang, "editorial", "settings.md")
        if not os.path.exists(settings_path):
            errors.append(f"Missing content/editorial/settings{suffix}.md")
            continue
        try:
            settings[lang], _ = read_front_matter(settings_path)
        except Exception as exc:
            errors.append(str(exc))
            continue
        for key in ("brand", "description", "author", "affiliate_link", "affiliate_cta", "affiliate_cta_bonus", "locale", "ui", "verification_status"):
            if not settings[lang].get(key):
                errors.append(f"{settings_path}: missing {key}")
        if settings[lang].get("layout_variant") not in {"proof-first", "editorial", "compact"}:
            errors.append(f"{settings_path}: invalid layout_variant")

    if "de" in settings:
        reference_keys = set(settings["de"].get("ui", {}))
        for lang in ("en", "pl", "es", "pt", "ja"):
            if lang in settings:
                missing = sorted(reference_keys - set(settings[lang].get("ui", {})))
                if missing:
                    errors.append(f"content/editorial/settings.{lang}.md: missing ui keys {missing}")
    verification_status = settings.get("de", {}).get("verification_status")
    if verification_status == "pending":
        warnings.append("verification_status is pending; source review is still required")
    elif verification_status not in {"verified", "confirmed"}:
        warnings.append("verification_status should be pending, confirmed or verified")

    configured = tuple(cfg.get("languages", {}).keys())
    if configured != configured:  # keep simple deterministic flow for older Python linters
        pass
    missing_lang_config = [lang for lang in LANGS if lang not in configured]
    if missing_lang_config:
        errors.append(f"Missing language config: {missing_lang_config}")

    pages = defaultdict(dict)
    for path in glob.glob(os.path.join(root, "content", "**", "*.md"), recursive=True):
        # Editorial settings are configuration records rendered with build.render=never, not public pages.
        if os.path.basename(os.path.dirname(path)) == "editorial" and os.path.basename(path).startswith("settings"):
            continue
        try:
            fm, _ = read_front_matter(path)
        except Exception as exc:
            errors.append(str(exc))
            continue
        # Files marked build.render=never are source/configuration records, not public pages.
        build_settings = fm.get("build", {})
        if isinstance(build_settings, dict) and str(build_settings.get("render", "")).strip("'\"") == "never":
            continue
        key, lang = page_key(path, os.path.join(root, "content"))
        pages[key][lang] = path

        missing = REQUIRED_FRONT_MATTER - set(fm)
        if missing:
            errors.append(f"{path}: missing front matter keys {sorted(missing)}")

        if lang in ("en", "pl", "es", "pt", "ja") and re.search(r"\]\(/(?:en/|pl/|es/|pt/|ja/|de/)", open(path, encoding="utf-8").read()):
            errors.append(f"{path}: hardcoded language-prefixed internal link")

    for key, variants in sorted(pages.items()):
        for lang in LANGS:
            if lang not in variants:
                errors.append(f"{key}: missing {lang} translation")
        bodies = {}
        for lang, path in variants.items():
            try:
                _, body = read_front_matter(path)
                normalized = re.sub(r"\s+", " ", body).strip()
                bodies[lang] = normalized
            except Exception:
                continue
        for a in LANGS:
            for b in LANGS:
                if a < b and a in bodies and b in bodies and bodies[a] == bodies[b] and len(bodies[a]) > 80:
                    warnings.append(f"{key}: {a}/{b} bodies are identical; review translation")

    production_ready = bool(cfg.get("params", {}).get("productionReady", False))
    indexing_enabled = bool(cfg.get("params", {}).get("indexingEnabled", False))
    if production_ready and not indexing_enabled:
        errors.append("indexingEnabled must be true when productionReady=true")
    elif not indexing_enabled:
        warnings.append("Indexing is intentionally disabled until legal/operator/source details are verified")
    author_profiles_indexable = bool(cfg.get("params", {}).get("authorProfilesIndexable", False))
    show_external_ratings = bool(cfg.get("params", {}).get("showExternalRatings", False))
    if production_ready:
        de_settings = settings.get("de", {})
        if not de_settings.get("email") or not de_settings.get("address"):
            errors.append("productionReady=true requires real email and address in content/editorial/settings.md")
        if "promo-fieryplay.com" in str(de_settings.get("affiliate_link", "")):
            errors.append("productionReady=true but affiliate_link still uses the template destination")
        # productionReady selects production-mode site behaviour; it is not a
        # claim that every source record or offer has already been verified.
        # Incomplete source records must remain visibly unverified in content,
        # but they must not prevent Hugo from building or deploying the site.
        if de_settings.get("verification_status") != "verified":
            warnings.append(
                "productionReady=true while verification_status is not verified; "
                "keep affected claims and offers clearly marked as unverified"
            )
        registry_path = os.path.join(root, "data", "site", "source-registry.yaml")
        registry = load_yaml(registry_path) if os.path.exists(registry_path) else {}
        if registry.get("status") != "verified":
            warnings.append(
                "source-registry.yaml is not fully verified; source-dependent data "
                "must not be presented as confirmed"
            )
        for record in registry.get("records", []):
            missing = [k for k in ("source_url", "last_verified") if not record.get(k)]
            if missing:
                warnings.append(
                    f"source-registry record {record.get('key', 'unknown')} missing: "
                    f"{', '.join(missing)}"
                )
    if author_profiles_indexable:
        author_files = glob.glob(os.path.join(root, "content", "de", "authors", "author-*.md"))
        unconfirmed = []
        for author_path in author_files:
            if re.search(r"\.(en|pl|es|pt|ja|fr)\.md$", author_path):
                continue
            author_data, _ = read_front_matter(author_path)
            if not author_data.get("contributor_confirmed"):
                unconfirmed.append(author_data.get("title", os.path.basename(author_path)))
        if unconfirmed:
            errors.append(f"authorProfilesIndexable=true requires contributor confirmation for: {', '.join(unconfirmed)}")
    if show_external_ratings:
        reviews_path = os.path.join(root, "data", "site", "reviews.yaml")
        reviews_data = load_yaml(reviews_path) if os.path.exists(reviews_path) else {}
        editorial = reviews_data.get("editorial", {})
        if not editorial.get("score") or not reviews_data.get("sources"):
            errors.append("showExternalRatings=true requires a documented score and at least one source in data/site/reviews.yaml")

    for path in glob.glob(os.path.join(root, "layouts", "**", "*.html"), recursive=True):
        text = open(path, encoding="utf-8").read()
        for marker in HARDCODED_TEMPLATE_MARKERS:
            if marker in text:
                errors.append(f"{path}: hardcoded UI marker remains: {marker}")

    if os.path.exists(os.path.join(root, "public")):
        warnings.append("public/ exists; existing generated output is left untouched")

    # Legal/privacy/cookie pages are intentionally indexable in this build.
    for base in ("cookies", "datenschutz", "impressum"):
        for lang in LANGS:
            fn = f"content/{lang}/{base}.md"
            path = os.path.join(root, fn)
            if os.path.exists(path):
                fm, _ = read_front_matter(path)
                if fm.get("noindex") is True:
                    errors.append(f"{fn}: must not be noindex in indexable build")
                if isinstance(fm.get("sitemap"), dict) and fm["sitemap"].get("disable") is True:
                    errors.append(f"{fn}: must not disable sitemap in indexable build")

    print(f"Checked {len(pages)} logical pages x {len(LANGS)} languages")
    if warnings:
        print("\nWarnings:")
        for item in warnings:
            print(" -", item)

    if errors:
        print("\nErrors:")
        for item in errors:
            print(" -", item)
        return 1

    print("\nPASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
