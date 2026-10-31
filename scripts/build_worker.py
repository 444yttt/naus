"""Bundle site/ into a single Worker module (dist/worker.js) for direct upload via the Cloudflare API.

Usage: python3 scripts/build_worker.py
"""
import base64, json, os

ROOT = os.path.join(os.path.dirname(__file__), '..', 'site')
MIME = {'.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'application/javascript; charset=utf-8',
        '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.txt': 'text/plain; charset=utf-8', '.xml': 'application/xml; charset=utf-8'}

files = {}
KV_FILES = {'/og.jpg'}  # served from the NAUS_FILES KV namespace (uploaded separately) to keep the script small

for d, _, names in os.walk(ROOT):
    for n in names:
        path = os.path.join(d, n)
        rel = '/' + os.path.relpath(path, ROOT).replace(os.sep, '/')
        if rel in KV_FILES:
            continue
        data, t = open(path, 'rb').read(), MIME[os.path.splitext(n)[1]]
        # text stays as text (smaller upload); binaries are base64
        files[rel] = {'s': data.decode('utf-8'), 't': t} if t.startswith(('text/', 'application/')) else {'b': base64.b64encode(data).decode(), 't': t}

worker = '''const F = %s;
const dec = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));
const send = (p, status = 200) => new Response(F[p].s !== undefined ? F[p].s : dec(F[p].b), { status, headers: { 'content-type': F[p].t, 'cache-control': p.endsWith('.html') ? 'no-cache' : 'public, max-age=3600' } });
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    let p = decodeURIComponent(url.pathname);
    if (p === '/og.jpg' && env.NAUS_FILES) {
      const img = await env.NAUS_FILES.get('og.jpg', 'arrayBuffer');
      if (img) return new Response(img, { headers: { 'content-type': 'image/jpeg', 'cache-control': 'public, max-age=86400' } });
    }
    if (p.endsWith('/')) p += 'index.html';
    if (F[p]) return send(p);
    if (F[p + '/index.html']) return Response.redirect(url.origin + url.pathname + '/' + url.search, 301);
    return send('/404.html', 404);
  }
};
''' % json.dumps(files, ensure_ascii=False)

out = os.path.join(os.path.dirname(__file__), '..', 'dist')
os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'worker.js'), 'w', encoding='utf-8').write(worker)
print('dist/worker.js', len(worker), 'bytes,', len(files), 'files')
