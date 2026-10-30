#!/usr/bin/env python3
"""Static SEO/content audit for Instant Casino Hugo project; does not replace a Hugo build."""
from __future__ import annotations
from pathlib import Path
import argparse, re, sys, collections
try:
    import yaml
except ImportError:
    yaml = None
LANGS = ('de','en','pl','es','pt','ja')
SUFFIX = {l: ('' if l == 'de' else f'.{l}') for l in LANGS}

def parse(path: Path):
    text = path.read_text(encoding='utf-8')
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)$', text, re.S)
    if not m: return {}, text, text
    raw, body = m.group(1), m.group(2)
    if yaml:
        try: data = yaml.safe_load(raw) or {}
        except Exception as e: raise ValueError(f'{path}: YAML front matter: {e}')
    else:
        # Dependency-free fallback for environments without PyYAML. Parse top-level
        # scalar keys and the nested `ui:` string map used by this project. The old
        # fallback stored `ui:` as an empty string, causing seo-audit.py to crash
        # when it tried to compare translated UI keys.
        data = {}
        raw_lines = raw.splitlines()
        for line in raw_lines:
            if line and not line[0].isspace() and ':' in line:
                k, v = line.split(':', 1)
                data[k.strip()] = v.strip().strip("'\"")
        # Read the two nested mappings this audit depends on (`build` and `ui`).
        # Other front-matter fields used by these checks are top-level scalars.
        for section in ('build', 'ui'):
            nested = {}
            in_section = False
            for line in raw_lines:
                if re.match(rf'^{re.escape(section)}:\s*(?:#.*)?$', line):
                    in_section = True
                    continue
                if in_section and line and not line[0].isspace():
                    in_section = False
                if not in_section:
                    continue
                item = re.match(r'^\s{2,}([A-Za-z0-9_-]+):\s*(.*)$', line)
                if item:
                    key, value = item.group(1), item.group(2).strip()
                    nested[key] = value.strip("'\"")
            data[section] = nested
    return data, body, text

def page_lang(path: Path):
    # Active content is organized as content/<language>/<relative-page>.md
    parts = path.parts
    for i, part in enumerate(parts[:-1]):
        if part == 'content' and i + 1 < len(parts) and parts[i + 1] in LANGS:
            return parts[i + 1]
    return 'de'

def is_settings(path: Path):
    return path.parent.name == 'editorial' and path.name.startswith('settings')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1]); args=ap.parse_args()
    root=args.root.resolve(); content=root/'content'; errors=[]; warnings=[]
    files=list(content.rglob('*.md'))
    by_lang={l:[] for l in LANGS}; groups=collections.defaultdict(dict)
    for p in files:
        if is_settings(p): continue
        lang=page_lang(p)
        fm,body,whole=parse(p)
        render=fm.get('build',{}).get('render') if isinstance(fm.get('build'),dict) else None
        if render=='never':
            if p.parent.name!='editorial': errors.append(f'Public content unexpectedly render: never: {p.relative_to(root)}')
            continue
        rel=p.relative_to(content).as_posix()
        parts=Path(rel).parts
        stem=Path(*parts[1:]).with_suffix('').as_posix() if parts[0] in LANGS else Path(rel).with_suffix('').as_posix()
        groups[stem][lang]=p; by_lang[lang].append((p,fm,body,whole))
        for key in ('title','description','seo_title','type'):
            if not fm.get(key): errors.append(f'{p.relative_to(root)} missing {key}')
        if fm.get('noindex') is True: errors.append(f'Public page is noindex: {p.relative_to(root)}')
        if len(str(fm.get('seo_title',''))) > 75: warnings.append(f'Title >75 chars ({len(str(fm.get("seo_title")))}): {p.relative_to(root)}')
        if len(str(fm.get('description',''))) > 180: warnings.append(f'Description >180 chars ({len(str(fm.get("description")))}): {p.relative_to(root)}')
        if len(re.sub(r'\s+',' ',body).strip()) < 300 and p.name not in ('_index.md','_index.en.md','_index.pl.md','_index.es.md','_index.pt.md','_index.ja.md'):
            warnings.append(f'Body <300 chars: {p.relative_to(root)}')
        if 'TODO' in body or 'TBD' in body or '[Kontaktadresse vor Veröffentlichung ergänzen]' in body or '[Ladungsfähige Anschrift vor Veröffentlichung ergänzen]' in body:
            warnings.append(f'Possible release placeholder: {p.relative_to(root)}')
        if re.search(r'(?i)lorem ipsum|dummy data|fake review|demo data', body): warnings.append(f'Suspicious placeholder phrase: {p.relative_to(root)}')
    print(f'Public Markdown files by language: { {l:len(by_lang[l]) for l in LANGS} }')
    print(f'Logical page groups: {len(groups)}')
    for key, variants in groups.items():
        missing=set(LANGS)-set(variants)
        if missing: errors.append(f'Missing translations {sorted(missing)}: {key}')
    for lang, pages in by_lang.items():
        for key in ('seo_title','description'):
            seen=collections.defaultdict(list)
            for p,fm,body,_ in pages:
                val=str(fm.get(key,'')).strip().lower()
                if val: seen[val].append(p)
            for val,ps in seen.items():
                if len(ps)>1: errors.append(f'Duplicate {key} [{lang}] {val[:70]}: '+', '.join(p.name for p in ps[:5]))
    # Verify relref targets resolve to a source Markdown file in the matching language family.
    all_sources={}
    for p in files:
        if is_settings(p): continue
        rel=p.relative_to(content).as_posix()
        parts=Path(rel).parts
        stem=Path(*parts[1:]).with_suffix('').as_posix() if parts[0] in LANGS else Path(rel).with_suffix('').as_posix()
        lang=page_lang(p)
        all_sources.setdefault(stem,set()).add(lang)
    for p in files:
        if is_settings(p): continue
        txt=p.read_text(encoding='utf-8')
        lang=page_lang(p)
        for target in re.findall(r'\{\{<\s*relref\s+["\']([^"\']+)["\']\s*>\}\}',txt):
            key=target.strip('/')
            if key in ('','.') : continue
            if key not in all_sources and f'{key}/_index' not in all_sources: errors.append(f'Broken relref target {target}: {p.relative_to(root)}')
    # All localized settings must provide the same UI-key vocabulary; obvious shared UI fallbacks are warned.
    settings={}
    for lang in LANGS:
        p=root/'content'/lang/'editorial'/'settings.md'
        if not p.exists(): errors.append(f'Missing settings locale: {p.relative_to(root)}'); continue
        fm,_,_=parse(p); settings[lang]=fm
    if 'de' in settings:
        ref=set((settings['de'].get('ui') or {}).keys())
        for lang,fm in settings.items():
            keys=set((fm.get('ui') or {}).keys())
            if keys!=ref: errors.append(f'UI key mismatch {lang}: missing={sorted(ref-keys)}, extra={sorted(keys-ref)}')
        for lang in LANGS[1:]:
            dui=settings['de'].get('ui',{}); ui=settings.get(lang,{}).get('ui',{})
            # Meaningful text strings left exactly in German are usually translation misses; proper names and common terms are skipped.
            allow={'FAQ','Cookies','Cashback','LinkedIn','Website','Code','Minimum','Maximum','Instant Casino','RTP','SEO','VIP','Live','OK','EUR','USD','BTC','ETH','KYC','URL','JSON-LD'}
            same=[k for k,v in dui.items() if isinstance(v,str) and len(v)>10 and v==ui.get(k) and v not in allow and not re.search(r'^[0-9 ./+→–-]+$',v)]
            if same: warnings.append(f'{lang}: {len(same)} UI strings unchanged from German: {same[:12]}')
    cfg=(root/'hugo.toml').read_text(encoding='utf-8') if (root/'hugo.toml').exists() else ''
    for token in ["defaultContentLanguage = 'de'",'indexingEnabled = true','authorProfilesIndexable = true']:
        if token not in cfg: errors.append(f'Missing expected Hugo config: {token}')
    if 'baseURL' not in cfg or not re.search(r"baseURL\s*=\s*'https://[^']+'", cfg):
        errors.append('baseURL must be an HTTPS URL in hugo.toml')
    elif 'instantcasino.example' in cfg:
        warnings.append('baseURL is a reserved placeholder; set the confirmed production domain before launch')
    # Report source-only release limits.
    if not any('Hugo build not run' in w for w in warnings):
        warnings.append('Static audit does not execute Hugo; run the production build and inspect generated HTML before deploy.')
    print('\nWarnings:')
    for w in warnings: print(' - '+w)
    print('\nErrors:')
    for e in errors: print(' - '+e)
    print('\nRESULT:', 'FAIL' if errors else 'PASS (static checks only)')
    return 1 if errors else 0
if __name__=='__main__': raise SystemExit(main())
