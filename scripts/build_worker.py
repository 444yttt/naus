"""Build the naus-site Worker: it serves site/ from a pinned commit of this public repo via jsDelivr,
sets the right content types, and lets Cloudflare cache the files at the edge.

Usage: python3 scripts/build_worker.py [commit-sha]   (defaults to HEAD; the commit must be pushed)
"""
import json, os, subprocess, sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
sha = sys.argv[1] if len(sys.argv) > 1 else subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
files = sorted('/' + f[len('site/'):] for f in subprocess.check_output(['git', 'ls-files', 'site'], cwd=ROOT, text=True).split())

worker = '''const SHA = %s;
const FILES = new Set(%s);
const BASE = `https://cdn.jsdelivr.net/gh/444yttt/naus@${SHA}/site`;
const TYPES = { html: 'text/html; charset=utf-8', css: 'text/css; charset=utf-8', js: 'application/javascript; charset=utf-8', svg: 'image/svg+xml', jpg: 'image/jpeg', png: 'image/png', txt: 'text/plain; charset=utf-8', xml: 'application/xml; charset=utf-8' };

async function serve(p, status = 200) {
  const r = await fetch(BASE + p, { cf: { cacheEverything: true, cacheTtl: 31536000 } });
  if (!r.ok) return new Response('Not found', { status: 404 });
  const type = TYPES[p.split('.').pop()] || 'application/octet-stream';
  return new Response(r.body, { status, headers: {
    'content-type': type,
    'cache-control': type.startsWith('text/html') ? 'no-cache' : 'public, max-age=86400',
    'x-content-type-options': 'nosniff',
    'referrer-policy': 'strict-origin-when-cross-origin'
  } });
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    let p = decodeURIComponent(url.pathname);
    if (p.endsWith('/')) p += 'index.html';
    if (FILES.has(p)) return serve(p);
    if (FILES.has(p + '/index.html')) return Response.redirect(url.origin + url.pathname + '/' + url.search, 301);
    return serve('/404.html', 404);
  }
};
''' % (json.dumps(sha), json.dumps(files))

out = os.path.join(ROOT, 'dist')
os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'worker.js'), 'w', encoding='utf-8').write(worker)
print('dist/worker.js', len(worker), 'bytes, sha', sha[:10], ',', len(files), 'files')
