#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, re
from pathlib import Path

def normalize(text: str) -> str:
    text=re.sub(r'^---.*?---', '', text, flags=re.S|re.M)
    text=re.sub(r'[`*_#>|\[\]{}()\-]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip().lower()

def shingles(text, n=6):
    words=text.split()
    return set(' '.join(words[i:i+n]) for i in range(max(0,len(words)-n+1)))

def sim(a,b):
    A=shingles(normalize(a)); B=shingles(normalize(b))
    return len(A&B)/max(1,len(A|B))

def main():
    ap=argparse.ArgumentParser(description='Flag potentially over-duplicated site content before deployment.')
    ap.add_argument('root', nargs='+')
    args=ap.parse_args()
    files=[]
    for root in args.root:
        p=Path(root)
        for f in p.glob('content/**/*.md'):
            if f.name.startswith(('cookies','datenschutz','impressum')): continue
            files.append(f)
    for i,a in enumerate(files):
        for b in files[i+1:]:
            score=sim(a.read_text(encoding='utf-8'), b.read_text(encoding='utf-8'))
            if score>=0.82:
                print(f'WARNING high similarity {score:.0%}: {a} <-> {b}')
    print(f'Compared {len(files)} content files.')

if __name__=='__main__': main()
