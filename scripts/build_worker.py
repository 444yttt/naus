"""Bundle site/ into a single Worker module (dist/worker.js) for direct upload via the Cloudflare API.

Usage: python3 scripts/build_worker.py
"""
import base64, json, os

ROOT = os.path.join(os.path.dirname(__file__), '..', 'site')
MIME = {'.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'application/javascript; charset=utf-8'}

files = {}
for d, _, names in os.walk(ROOT):
    for n in names:
        path = os.path.join(d, n)
        rel = '/' + os.path.relpath(path, ROOT).replace(os.sep, '/')
        files[rel] = {'b': base64.b64encode(open(path, 'rb').read()).decode(), 't': MIME[os.path.splitext(n)[1]]}

worker = '''const F = %s;
const dec = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));
const send = (p, status = 200) => new Response(dec(F[p].b), { status, headers: { 'content-type': F[p].t, 'cache-control': p.endsWith('.html') ? 'no-cache' : 'public, max-age=3600' } });
export default {
  fetch(request) {
    const url = new URL(request.url);
    let p = decodeURIComponent(url.pathname);
    if (p.endsWith('/')) p += 'index.html';
    if (F[p]) return send(p);
    if (F[p + '/index.html']) return Response.redirect(url.origin + url.pathname + '/' + url.search, 301);
    return send('/404.html', 404);
  }
};
''' % json.dumps(files)

out = os.path.join(os.path.dirname(__file__), '..', 'dist')
os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'worker.js'), 'w').write(worker)
print('dist/worker.js', len(worker), 'bytes,', len(files), 'files')
