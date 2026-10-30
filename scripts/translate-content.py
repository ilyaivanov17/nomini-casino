#!/usr/bin/env python3
"""Translate Hugo Markdown pages from German into the configured site locales.

Provider: MyMemory by default, or LibreTranslate when TRANSLATE_PROVIDER=libre.
The script is intentionally conservative: it keeps the German source untouched,
protects URLs/code spans/fenced code and front-matter structure, and never claims
that a translation is verified by a human. Review generated content before release.
"""
from __future__ import annotations
import argparse, json, os, re, sys, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = {"en": "en-GB", "pl": "pl-PL", "es": "es-ES", "pt": "pt-PT", "ja": "ja-JP"}
TRANSLATABLE_KEYS = {"title", "description", "seo_title", "role", "bio", "label", "summary", "intro", "q", "a"}
PROTECTED_RE = re.compile(r'```[\s\S]*?```|`[^`]*`|https?://[^\s)\]}>]+|<[^>]+>', re.M)


def split_frontmatter(text: str):
    if not text.startswith('---\n'):
        return '', text
    end = text.find('\n---', 4)
    if end < 0:
        return '', text
    return text[4:end], text[end+4:].lstrip('\n')


def yaml_value(line: str):
    m = re.match(r'^(\s*)([A-Za-z0-9_-]+):(\s*)(.*)$', line)
    return m


def translate_api(text: str, target: str, provider: str):
    if not text.strip(): return text
    last = None
    for attempt in range(5):
        try:
            if provider == 'libre':
                endpoint = os.environ.get('LIBRETRANSLATE_URL', 'https://libretranslate.com/translate')
                payload = json.dumps({"q": text, "source": "de", "target": target.split('-')[0], "format": "text", "api_key": os.environ.get('LIBRETRANSLATE_API_KEY', '')}).encode()
                req = urllib.request.Request(endpoint, data=payload, headers={"Content-Type": "application/json", "User-Agent": "Hugo-Multilingual-Content/1.0"})
                with urllib.request.urlopen(req, timeout=30) as resp: data = json.loads(resp.read().decode('utf-8'))
                return data['translatedText']
            query = urllib.parse.urlencode({"q": text, "langpair": f"de|{target.split('-')[0]}"})
            req = urllib.request.Request('https://api.mymemory.translated.net/get?' + query, headers={"User-Agent": "Hugo-Multilingual-Content/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp: data = json.loads(resp.read().decode('utf-8'))
            if data.get('responseStatus') not in (200, '200'):
                raise RuntimeError(data.get('responseDetails', 'Translation provider returned an error'))
            result = data.get('responseData', {}).get('translatedText', '')
            if not result: raise RuntimeError('Empty translation response')
            return result
        except Exception as exc:
            last = exc
            time.sleep(min(2 ** attempt, 20))
    raise RuntimeError(f"translation failed for {target}: {last}")


def translate_preserving_markup(text: str, target: str, provider: str):
    # Preserve fenced code blocks and inline technical tokens with placeholders.
    protected = []
    def keep(m):
        protected.append(m.group(0)); return f' ZXQPROTECTED{len(protected)-1}QXZ '
    masked = PROTECTED_RE.sub(keep, text)
    # Translate paragraph-by-paragraph to avoid provider length limits and keep Markdown layout.
    chunks = re.split(r'(\n\s*\n)', masked)
    out=[]
    for chunk in chunks:
        if not chunk.strip() or re.fullmatch(r'\n\s*\n', chunk):
            out.append(chunk); continue
        # Split very long paragraphs into sentence chunks below provider limits.
        if len(chunk) <= 430:
            out.append(translate_api(chunk, target, provider))
        else:
            pieces = re.split(r'(?<=[.!?。！？])\s+', chunk)
            buf=''; translated=[]
            for piece in pieces:
                if buf and len(buf)+len(piece)+1 > 400:
                    translated.append(translate_api(buf, target, provider)); buf=''
                buf = (buf+' '+piece).strip()
            if buf: translated.append(translate_api(buf, target, provider))
            out.append(' '.join(translated))
    result=''.join(out)
    for i, token in enumerate(protected): result=result.replace(f'ZXQPROTECTED{i}QXZ', token)
    return result


def translate_frontmatter(front: str, target: str, provider: str):
    lines=front.splitlines(); out=[]; parent=''
    for line in lines:
        m=yaml_value(line)
        if not m:
            out.append(line); continue
        indent,key,space,value=m.groups()
        if not indent:
            parent=key
        if (key in TRANSLATABLE_KEYS or (parent == 'ui' and value) or (parent in ('menu','footer_areas','footer_legal') and key == 'name')) and value and not value.startswith(('{','[','|','>')):
            # Translate scalar text only; retain YAML quoting style and don't touch IDs/URLs.
            quote='"' if value.startswith('"') and value.endswith('"') else ("'" if value.startswith("'") and value.endswith("'") else '')
            raw=value[1:-1] if quote else value
            if raw and not raw.startswith('http'):
                translated=translate_preserving_markup(raw, target, provider).replace('"','\\"') if quote=='"' else translate_preserving_markup(raw, target, provider)
                value=f'{quote}{translated}{quote}' if quote else translated
        out.append(f'{indent}{key}:{space}{value}')
    return '\n'.join(out)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root', default=str(ROOT))
    ap.add_argument('--overwrite', action='store_true', help='replace existing translations; default is create missing files only')
    ap.add_argument('--limit', type=int, default=0, help='translate at most N source pages, for testing')
    ap.add_argument('--provider', choices=['mymemory','libre'], default=os.environ.get('TRANSLATE_PROVIDER','mymemory'))
    ap.add_argument('--langs', default='en,pl,es,pt,ja')
    args=ap.parse_args(); root=Path(args.root).resolve(); langs=[x.strip() for x in args.langs.split(',') if x.strip()]
    sources=sorted(p for p in (root/'content').rglob('*.md') if not re.search(r'\.(en|pl|es|pt|ja|fr)\.md$', p.name))
    if args.limit: sources=sources[:args.limit]
    created=0; skipped=0; failed=[]
    for src in sources:
        original=src.read_text(encoding='utf-8')
        front,body=split_frontmatter(original)
        for lang in langs:
            if lang not in LANGS:
                print(f'SKIP unsupported locale: {lang}'); continue
            suffix=f'.{lang}.md'; target_path=src.with_name(src.stem+suffix)
            if target_path.exists() and not args.overwrite:
                skipped+=1; continue
            try:
                new_front=translate_frontmatter(front, LANGS[lang], args.provider) if front else ''
                new_body=translate_preserving_markup(body, LANGS[lang], args.provider)
                target_path.write_text(('---\n'+new_front+'\n---\n\n' if front else '')+new_body.rstrip()+'\n', encoding='utf-8')
                created+=1; print(f'OK [{lang}] {target_path.relative_to(root)}')
            except Exception as exc:
                failed.append((str(target_path.relative_to(root)), str(exc)))
                print(f'ERROR [{lang}] {target_path.relative_to(root)}: {exc}', file=sys.stderr)
    print(f'Finished: written={created}, skipped_existing={skipped}, failed={len(failed)}')
    if failed:
        print('Failures can be retried by rerunning the command; existing successful files are skipped unless --overwrite is set.')
        sys.exit(1)

if __name__=='__main__': main()
