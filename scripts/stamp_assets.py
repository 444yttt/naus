"""Add a content-hash version (?v=) to the CSS/JS references in every page so browsers never keep a stale copy.

Run before committing: python3 scripts/stamp_assets.py
"""
import hashlib, os, re

SITE = os.path.join(os.path.dirname(__file__), '..', 'site')
ver = {}
for name in ('style.css', 'main.js'):
    ver[name] = hashlib.sha256(open(os.path.join(SITE, name), 'rb').read()).hexdigest()[:10]

for d, _, files in os.walk(SITE):
    for f in files:
        if not f.endswith('.html'):
            continue
        p = os.path.join(d, f)
        s = open(p, encoding='utf-8').read()
        t = s
        for name, v in ver.items():
            t = re.sub(r'((?:href|src)="(?:\.\./|/)?' + re.escape(name) + r')(\?v=[0-9a-f]+)?"', r'\1?v=' + v + '"', t)
        if t != s:
            open(p, 'w', encoding='utf-8').write(t)
            print('stamped', os.path.relpath(p, SITE))
print(ver)
