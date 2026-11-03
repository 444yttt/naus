"""Project the layout (floor-plan metres) into each photo and measure how well the tile grid fits.
usage: project.py layout.json option data_dir out_dir
data_dir holds v*.jpg, v*_calib.json, v*_lines.npy, cams.json (from the calibration step)."""
import json, sys, math, numpy as np, cv2
L = json.load(open(sys.argv[1])); opt = sys.argv[2]; D = sys.argv[3].rstrip('/') + '/'; O = sys.argv[4].rstrip('/') + '/'
cams = json.load(open(D + 'cams.json'))
TILE = .6

def proj(c, cam, h, pts):
    """world (x, y, z) metres -> pixels; returns None for points behind the camera"""
    K = np.array(c['K']); R = np.array(c['Rcw'])
    rel = np.c_[pts[:, 0] - cam[0], pts[:, 1] - cam[1], pts[:, 2] - h]
    pc = (R @ rel.T).T
    ok = pc[:, 2] > .05
    uv = (K @ pc.T).T; uv = uv[:, :2] / uv[:, 2:3]
    return uv, ok

# grid phase in the shared frame comes from view 1 (all views were registered to it)
c1 = json.load(open(D + 'v1_calib.json')); h1 = cams['v1']['h']; cam1 = np.array(cams['v1']['cam'])
def cphase(a): t = 2 * np.pi * a / TILE; return np.angle(np.mean(np.exp(1j * t))) * TILE / (2 * np.pi)
phY = cphase(np.array([a for a, _ in c1['joints']['A']]) * h1 + cam1[1])
phX = cphase(np.array([a for a, _ in c1['joints']['B']]) * h1 + cam1[0])

HEIGHT = {'dining_table': .74, 'chair': .8, 'sofa': .75, 'coffee_table': .35, 'rug': .012, 'tv_eclipse65': 1.37,
          'speaker_beolab28': 1.26, 'lounge_chair': .85}
COL = {'dining_table': (60, 110, 160), 'chair': (90, 140, 180), 'sofa': (215, 215, 205), 'coffee_table': (50, 50, 60), 'rug': (150, 170, 190),
       'tv_eclipse65': (25, 25, 25), 'speaker_beolab28': (40, 40, 40), 'lounge_chair': (40, 70, 110)}

def boxes():
    items = L['options'][opt]['items']; out = []
    table = next(i for i in items if i['type'] == 'dining_table')
    for it in items:
        if it['type'] != 'chairs': out.append((it['type'], it['x'], it['y'], it['w'], it['d'], it['rot'])); continue
        tw, td = table['w'], table['d']; Lg = max(tw, td); n = it['n_side']
        for i in range(n):
            u = -Lg / 2 + Lg * (i + .5) / n
            for s in (-1, 1):
                out.append(('chair', table['x'] + (u if tw >= td else s * (tw / 2 + .3)), table['y'] + (s * (td / 2 + .3) if tw >= td else u), .5, .5, 0))
    return out

def corners(x, y, w, d, rot, z0, z1):
    a = math.radians(rot); c, s = math.cos(a), math.sin(a)
    fp = [(x + c * u - s * v, y + s * u + c * v) for u, v in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))]
    return np.array([(p[0], p[1], z0) for p in fp] + [(p[0], p[1], z1) for p in fp])

report = {}
for v in sorted(cams):
    c = json.load(open(D + v + '_calib.json')); cam = np.array(cams[v]['cam']); h = cams[v]['h']
    img = cv2.imread(D + v + '.jpg'); H, W = img.shape[:2]; vis = img.copy()
    # 1) projected tile grid vs detected floor joints
    segs = np.load(D + v + '_lines.npy'); errs = {'x': [], 'y': []}
    gx = phX + TILE * np.arange(-20, 21); gy = phY + TILE * np.arange(-20, 21)
    lines = []
    RM = L['room']; x0r, x1r, y0r, y1r = RM['right_wall_x'], RM['W2_glass_x'] - .3, RM['top_wall_y'], RM['W1_glass_y'] - .3
    for X in gx[(gx > x0r) & (gx < x1r)]: lines.append(('x', np.array([[X, y0r, 0], [X, y1r, 0]])))
    for Y in gy[(gy > y0r) & (gy < y1r)]: lines.append(('y', np.array([[x0r, Y, 0], [x1r, Y, 0]])))
    plines = []
    for fam, P in lines:
        # clip the segment to the part in front of the camera, sampled
        t = np.linspace(0, 1, 200)[:, None]; pts = P[0] + t * (P[1] - P[0]); uv, ok = proj(c, cam, h, pts)
        uv = uv[ok]
        inside = (uv[:, 0] > -W) & (uv[:, 0] < 2 * W) & (uv[:, 1] < 2 * H)
        uv = uv[inside]
        if len(uv) < 2: continue
        a, b = uv[0], uv[-1]; plines.append((fam, a, b))
        cv2.line(vis, tuple(map(int, a)), tuple(map(int, b)), (0, 200, 255), 1)
    for s in segs:
        ang = abs(math.degrees(math.atan2(s[3] - s[1], s[2] - s[0]))) % 180
        if min(s[1], s[3]) < H * .55 or abs(ang - 90) < 12: continue
        m = np.array([(s[0] + s[2]) / 2, (s[1] + s[3]) / 2]); dvec = np.array([s[2] - s[0], s[3] - s[1]]); dvec /= np.linalg.norm(dvec)
        best = None
        for fam, a, b in plines:
            e = b - a; e /= np.linalg.norm(e)
            if abs(e @ dvec) < .99: continue
            nrm = np.array([-e[1], e[0]]); dist = max(abs((np.array(s[:2]) - a) @ nrm), abs((np.array(s[2:]) - a) @ nrm))
            if best is None or dist < best[0]: best = (dist, fam)
        if best and best[0] < 25:
            errs[best[1]].append(best[0]); cv2.line(vis, (int(s[0]), int(s[1])), (int(s[2]), int(s[3])), (255, 0, 255), 3)
    # 2) furniture boxes (footprint filled, edges drawn), far to near
    RM = L['room']; wall = (60, 200, 60)
    for P in ([[x0r, RM['W1_glass_y'] - .3, 0], [RM['W2_glass_x'] - .3, RM['W1_glass_y'] - .3, 0]], [[RM['W2_glass_x'] - .3, RM['W1_glass_y'] - .3, 0], [RM['W2_glass_x'] - .3, y0r, 0]],
              [[x0r, y0r, 0], [x0r, RM['W1_glass_y'] - .3, 0]]):
        P = np.array(P, float); t = np.linspace(0, 1, 80)[:, None]; Q = P[0] + t * (P[1] - P[0]); uv, ok = proj(c, cam, h, Q); uv = uv[ok]
        if len(uv) > 1: cv2.polylines(vis, [uv.astype(np.int32)], False, wall, 5)
    faces = []
    for typ, x, y, w, d, rot in boxes():
        P = corners(x, y, w, d, rot, 0, HEIGHT[typ]); uv, ok = proj(c, cam, h, P)
        if not ok.all(): continue
        rel = P - np.r_[cam, h]
        for fi, sh in (([4, 5, 6, 7], 1.0), ([0, 1, 5, 4], .75), ([1, 2, 6, 5], .6), ([2, 3, 7, 6], .75), ([3, 0, 4, 7], .6)):
            faces.append((-np.linalg.norm(rel[fi].mean(0)), typ, uv[fi].astype(np.int32), sh, uv[:4].astype(np.int32)))
    faces.sort(key=lambda f: f[0])
    over = vis.copy()
    for _, typ, poly, sh, foot in faces:
        col = tuple(int(c_ * sh) for c_ in COL[typ]); cv2.fillPoly(over, [poly], col); cv2.polylines(over, [poly], True, (25, 25, 25), 1)
    vis = cv2.addWeighted(over, .85, vis, .15, 0)
    for _, typ, poly, sh, foot in faces:
        for p in foot: cv2.circle(vis, tuple(p), 5, (0, 0, 255), -1)
    rr = json.load(open(D + 'refine_report.json')).get(v, {}) if __import__('os').path.exists(D + 'refine_report.json') else {}
    allerr = np.array(errs['x'] + errs['y'])
    r = {'fit_rms_px': rr.get('rms_after'), 'fit_median_px': rr.get('median_abs_after'), 'fit_segments': rr.get('segments'),'n': int(len(allerr)), 'rms_px': round(float(np.sqrt((allerr ** 2).mean())), 2) if len(allerr) else None,
         'median_px': round(float(np.median(allerr)), 2) if len(allerr) else None, 'h_m': round(h, 3), 'f_px': round(c['f'], 1)}
    report[v] = r
    txt = f"{v}: f={r['f_px']}px h={r['h_m']}m  tile joints on grid: n={r['fit_segments']} rms={r['fit_rms_px']}px |median|={r['fit_median_px']}px"
    cv2.rectangle(vis, (0, 0), (W, 60), (255, 255, 255), -1); cv2.putText(vis, txt, (16, 42), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 0), 2)
    cv2.imwrite(O + v + '_check.jpg', vis, [cv2.IMWRITE_JPEG_QUALITY, 88])
json.dump(report, open(O + 'report.json', 'w'), indent=1); print(json.dumps(report, indent=1))
