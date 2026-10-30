#!/usr/bin/env python3
"""Report missing or suspiciously identical Markdown translations for Hugo locales."""
from pathlib import Path
import re, argparse
LANGS=('de','en','pl','es','pt','ja')
SUFFIXES=('.en.md','.pl.md','.es.md','.pt.md','.ja.md','.fr.md')

def is_render_never(path):
 text=path.read_text(encoding='utf-8')
 m=re.match(r'^---\s*\n(.*?)\n---', text, re.S)
 if not m: return False
 in_build=False
 for line in m.group(1).splitlines():
  if line and not line[0].isspace():
   in_build = bool(re.match(r'^build:\s*$', line))
  elif in_build:
   hit=re.match(r"^\s+render:\s*[\'\"]?never[\'\"]?\s*(?:#.*)?$", line)
   if hit: return True
 return False

def main():
 p=argparse.ArgumentParser(); p.add_argument('--root',default=str(Path(__file__).resolve().parent.parent)); a=p.parse_args(); root=Path(a.root)
 sources={}
 for f in (root/'content').rglob('*.md'):
  if f.parts[-2] == 'editorial' and f.name.startswith('settings'):
   continue
  if is_render_never(f):
   continue
  rel=f.relative_to(root/'content')
  parts=rel.parts
  if parts and parts[0] in LANGS:
   lang=parts[0]; stem=Path(*parts[1:]).with_suffix('')
  elif f.name.endswith(SUFFIXES):
   stem=Path(f.name.rsplit('.',2)[0]); lang=f.name.rsplit('.',2)[1]
  else: stem=Path(f.stem); lang='de'
  if lang not in LANGS: continue
  sources.setdefault(str(stem),{})[lang]=f
 missing=[]; same=[]
 for key, variants in sorted(sources.items()):
  for lang in LANGS:
   if lang not in variants: missing.append((key,lang))
  bodies={}
  for lang,f in variants.items():
   s=f.read_text(encoding='utf-8'); s=re.sub(r'^---[\s\S]*?---\s*','',s, count=1); bodies[lang]=re.sub(r'\s+',' ',s).strip().lower()
  for lang,body in bodies.items():
   if lang!='de' and body and body==bodies.get('de'): same.append((key,lang))
 print(f'Page groups: {len(sources)}; missing locale files: {len(missing)}; exact German-body duplicates: {len(same)}')
 for key,lang in missing: print(f'MISSING {lang}: {Path(key).relative_to(root)}')
 for key,lang in same: print(f'DUPLICATE {lang}: {Path(key).relative_to(root)}')
 return 1 if missing or same else 0
if __name__=='__main__': raise SystemExit(main())
