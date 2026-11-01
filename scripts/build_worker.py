"""Build the naus-site Worker: it serves site/ from a pinned commit of this public repo via jsDelivr,
sets the right content types, and lets Cloudflare cache the files at the edge.

Usage: python3 scripts/build_worker.py [commit-sha]   (defaults to HEAD; the commit must be pushed)
"""
import json, os, subprocess, sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
sha = sys.argv[1] if len(sys.argv) > 1 else subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
files = sorted('/' + f[len('site/'):] for f in subprocess.check_output(['git', 'ls-files', 'site'], cwd=ROOT, text=True).split())

worker = r'''// The commit to serve lives in KV (CONFIG, key "sha") so a release is a single KV write; %s is the fallback
const FALLBACK_SHA = %s;
const TYPES = { html: 'text/html; charset=utf-8', css: 'text/css; charset=utf-8', js: 'application/javascript; charset=utf-8', svg: 'image/svg+xml', jpg: 'image/jpeg', png: 'image/png', mp4: 'video/mp4', txt: 'text/plain; charset=utf-8', xml: 'application/xml; charset=utf-8' };
let BASE = '', checked = 0;
async function base(env) {
  if (!BASE || Date.now() - checked > 30000) {
    const sha = (env.CONFIG && await env.CONFIG.get('sha')) || FALLBACK_SHA;
    BASE = `https://cdn.jsdelivr.net/gh/444yttt/naus@${sha}/site`; checked = Date.now();
  }
  return BASE;
}

async function serve(env, p, status = 200, request) {
  // video needs byte ranges (iOS Safari will not play it otherwise)
  const range = request && request.headers.get('range');
  const r = await fetch((await base(env)) + p, { headers: range ? { range } : {}, cf: { cacheEverything: true, cacheTtl: 31536000 } });
  if (!r.ok) return null;
  const type = TYPES[p.split('.').pop()] || 'application/octet-stream';
  const headers = {
    'content-type': type,
    'cache-control': type.startsWith('text/html') ? 'no-cache' : 'public, max-age=86400',
    'x-content-type-options': 'nosniff',
    'referrer-policy': 'strict-origin-when-cross-origin',
    'accept-ranges': 'bytes'
  };
  for (const h of ['content-range', 'content-length']) if (r.headers.get(h)) headers[h] = r.headers.get(h);
  return new Response(r.body, { status: r.status === 206 ? 206 : status, headers });
}

const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
const clip = (v, n) => typeof v === 'string' ? v.trim().slice(0, n) : '';

// consult form -> D1 (table consultations); a hidden field and a per-connection hourly cap keep bots out
async function consult(request, env) {
  if (request.method !== 'POST') return json({ error: 'Method not allowed' }, 405);
  if (!(request.headers.get('content-type') || '').includes('application/json')) return json({ error: 'Invalid content type' }, 415);
  const origin = request.headers.get('origin');
  if (origin && new URL(origin).host !== new URL(request.url).host) return json({ error: 'Forbidden' }, 403);
  const raw = await request.text();
  if (raw.length > 9000000) return json({ error: '画像が大きすぎます' }, 413);
  let d; try { d = JSON.parse(raw); } catch { return json({ error: '送信内容を読み取れませんでした' }, 400); }
  if (d.website) return json({ ok: true });
  const row = { room: clip(d.room, 40), timing: clip(d.timing, 40), budget: clip(d.budget, 40), wish: clip(d.wish, 1500), name: clip(d.name, 80), email: clip(d.email, 200) };
  if (!row.room || !row.timing || !row.budget || !row.name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(row.email)) return json({ error: '未入力の項目があります' }, 400);
  // floor plan: a JPEG made on the device (max 1800px), kept private in KV; pins are fractions of the image size
  const jpeg = (v, max) => {
    const m = typeof v === 'string' && /^data:image\/jpeg;base64,([A-Za-z0-9+/=]+)$/.exec(v);
    if (!m) return null;
    const b = Uint8Array.from(atob(m[1]), c => c.charCodeAt(0));
    return b.length <= max && b[0] === 0xff && b[1] === 0xd8 ? b : null;
  };
  let planBytes = null;
  if (typeof d.plan === 'string' && d.plan) { planBytes = jpeg(d.plan, 2800000); if (!planBytes) return json({ error: '画像を読み取れませんでした' }, 400); }
  const refImgs = Array.isArray(d.refs) ? d.refs.slice(0, 3).map(r => jpeg(r, 1500000)) : [];
  if (refImgs.includes(null)) return json({ error: '画像を読み取れませんでした' }, 400);
  const pick = (v, n) => Array.isArray(v) ? v.slice(0, 12).map(x => clip(x, 40)).filter(Boolean).slice(0, n) : [];
  const list = v => { const a = pick(v, 12); return a.length ? JSON.stringify(a) : null; };
  const num = v => typeof v === 'number' && v >= 0 && v <= 1 ? Math.round(v * 1000) / 1000 : null;
  const pins = planBytes && Array.isArray(d.pins) ? d.pins.slice(0, 8).map(p => ({ x: num(p && p.x), y: num(p && p.y), note: clip(p && p.note, 120) })).filter(p => p.x !== null && p.y !== null) : [];
  const ip = request.headers.get('cf-connecting-ip') || '';
  const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode('naus-consult:' + ip)))].map(b => b.toString(16).padStart(2, '0')).join('');
  const recent = await env.DB.prepare("SELECT COUNT(*) AS n FROM consultations WHERE ip_hash = ? AND created_at > datetime('now', '-1 hour')").bind(hash).first();
  if (recent && recent.n >= 5) return json({ error: '短時間に送信が続いたため受け付けを止めています、しばらくしてからお試しください' }, 429);
  const id = crypto.randomUUID(), planKey = planBytes ? id + '.jpg' : null;
  if (planBytes) await env.PLANS.put(planKey, planBytes, { metadata: { type: 'image/jpeg' } });
  const refKeys = [];
  for (const [k, b] of refImgs.entries()) { const key = `${id}-ref${k + 1}.jpg`; await env.PLANS.put(key, b, { metadata: { type: 'image/jpeg' } }); refKeys.push(key); }
  await env.DB.prepare('INSERT INTO consultations (id, room, timing, budget, wish, name, email, ip_hash, user_agent, plan_key, pins, materials, styles, concerns, links, ref_keys) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)')
    .bind(id, row.room, row.timing, row.budget, row.wish, row.name, row.email, hash, clip(request.headers.get('user-agent'), 300), planKey, pins.length ? JSON.stringify(pins) : null,
      list(d.materials), list(d.styles), list(d.concerns), clip(d.links, 600) || null, refKeys.length ? JSON.stringify(refKeys) : null).run();
  return json({ ok: true }, 201);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/api/consult') {
      try { return await consult(request, env); }
      catch (e) { console.error('consult failed', e); return json({ error: '送信できませんでした、時間をおいてもう一度お試しください' }, 500); }
    }
    let p = decodeURIComponent(url.pathname);
    if (p.includes('..')) return (await serve(env, '/404.html', 404)) || new Response('Not found', { status: 404 });
    if (p.endsWith('/')) p += 'index.html';
    const hit = /\.[a-z0-9]+$/.test(p) ? await serve(env, p, 200, request) : null;
    if (hit) return hit;
    if (!/\.[a-z0-9]+$/.test(p) && await serve(env, p + '/index.html')) return Response.redirect(url.origin + url.pathname + '/' + url.search, 301);
    return (await serve(env, '/404.html', 404)) || new Response('Not found', { status: 404 });
  }
};
''' % (sha[:10], json.dumps(sha))

out = os.path.join(ROOT, 'dist')
os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'worker.js'), 'w', encoding='utf-8').write(worker)
print('dist/worker.js', len(worker), 'bytes, sha', sha[:10], ',', len(files), 'files')
# Release: after pushing, write the commit to KV namespace "naus-site-config" key "sha" (the Worker picks it up within ~30s).
