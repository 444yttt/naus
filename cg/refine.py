"""Refine each camera so the detected floor joints lie on the shared 0.6 m tile grid, measured in image pixels.
Parameters per view: position x/y, height, yaw/pitch/roll corrections, focal. Bounded; outlier segments are dropped.
usage: refine.py data_dir   (keeps the first calibration in v*_calib.orig.json and rewrites v*_calib.json, cams.json)"""
import sys, json, math, shutil, os, numpy as np
from scipy.optimize import least_squares
D = sys.argv[1].rstrip('/') + '/'; TILE = .6
cams = json.load(open(D + 'cams.json'))
for v in cams:
    if not os.path.exists(D + v + '_calib.orig.json'): shutil.copy(D + v + '_calib.json', D + v + '_calib.orig.json')
c1 = json.load(open(D + 'v1_calib.orig.json')); h1 = cams['v1']['h']; cam1 = np.array(cams['v1']['cam'])
def cphase(a): t = 2 * np.pi * a / TILE; return np.angle(np.mean(np.exp(1j * t))) * TILE / (2 * np.pi)
phY = cphase(np.array([a for a, _ in c1['joints']['A']]) * h1 + cam1[1]); phX = cphase(np.array([a for a, _ in c1['joints']['B']]) * h1 + cam1[0])
def rot(ax, a):
    c, s = math.cos(a), math.sin(a)
    return {'x': np.array([[1, 0, 0], [0, c, -s], [0, s, c]]), 'y': np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]), 'z': np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])}[ax]
out = {}
for v in sorted(cams):
    c = json.load(open(D + v + '_calib.orig.json')); K0 = np.array(c['K']); R0 = np.array(c['Rcw']); cx, cy = K0[0, 2], K0[1, 2]; H = 2 * cy
    segs = np.load(D + v + '_lines.npy')
    ang = np.degrees(np.arctan2(segs[:, 3] - segs[:, 1], segs[:, 2] - segs[:, 0])) % 180
    segs = segs[(np.minimum(segs[:, 1], segs[:, 3]) > H * .5) & (np.abs(ang - 90) > 12)]
    p0 = np.array([*cams[v]['cam'], cams[v]['h'], 0, 0, 0, c['f']])
    def model(p):
        K = np.array([[p[6], 0, cx], [0, p[6], cy], [0, 0, 1]]); R = R0 @ rot('z', p[3]) @ rot('x', p[4]) @ rot('y', p[5]); return K, R, p[:2], p[2]
    def proj(K, R, cam, h, P):
        pc = (R @ np.c_[P[:, 0] - cam[0], P[:, 1] - cam[1], P[:, 2] - h].T).T; uv = (K @ pc.T).T; return uv[:, :2] / uv[:, 2:3], pc[:, 2]
    def backproject(K, R, cam, h, uv):
        w = (R.T @ np.linalg.inv(K) @ np.c_[uv, np.ones(len(uv))].T).T; t = -h / w[:, 2]; return np.c_[cam[0] + w[:, 0] * t, cam[1] + w[:, 1] * t], t
    # assign every segment to one grid line (family + index) from the starting pose
    K, R, cam, h = model(p0)
    A, ta = backproject(K, R, cam, h, segs[:, :2]); B, tb = backproject(K, R, cam, h, segs[:, 2:])
    good = (ta > 0) & (tb > 0); d = B - A
    fam = np.abs(d[:, 0]) > np.abs(d[:, 1])                       # True: runs along x -> constant y
    val = np.where(fam, (A[:, 1] + B[:, 1]) / 2, (A[:, 0] + B[:, 0]) / 2); ph = np.where(fam, phY, phX)
    idx = np.round((val - ph) / TILE); off = np.abs(val - ph - idx * TILE)
    straight = np.where(fam, np.abs(d[:, 1]), np.abs(d[:, 0])) / np.maximum(np.hypot(*d.T), 1e-6) < .05
    keep = good & straight & (off < .07) & (np.hypot(*d.T) > .15)
    segs, fam, gval = segs[keep], fam[keep], (ph + idx * TILE)[keep]
    def resid(p):
        K, R, cam, h = model(p); r = []
        for s, f_, g in zip(segs, fam, gval):
            P = np.array([[-15, g, 0], [8, g, 0]]) if f_ else np.array([[g, -15, 0], [g, 8, 0]])
            # clip the grid line to the part in front of the camera before projecting
            t = np.linspace(0, 1, 60)[:, None]; Q = P[0] + t * (P[1] - P[0]); uv, z = proj(K, R, cam, h, Q); uv = uv[z > .2]
            a, b = uv[0], uv[-1]; e = (b - a) / np.linalg.norm(b - a); n = np.array([-e[1], e[0]])
            r += [(s[:2] - a) @ n, (s[2:] - a) @ n]
        return np.array(r)
    r0 = resid(p0)
    lo = p0 - [.3, .3, .15, .03, .03, .03, p0[6] * .08]; hi = p0 + [.3, .3, .15, .03, .03, .03, p0[6] * .08]
    sol = least_squares(resid, p0, bounds=(lo, hi), loss='soft_l1', f_scale=3, x_scale=[.05, .05, .02, .003, .003, .003, 10])
    r1 = sol.fun; K, R, cam, h = model(sol.x)
    c['K'] = K.tolist(); c['Rcw'] = R.tolist(); c['f'] = float(K[0, 0]); json.dump(c, open(D + v + '_calib.json', 'w'))
    cams[v].update(cam=[float(cam[0]), float(cam[1])], h=float(h), f=float(K[0, 0]))
    out[v] = dict(segments=int(len(segs)), rms_before=round(float(np.sqrt((r0 ** 2).mean())), 2), rms_after=round(float(np.sqrt((r1 ** 2).mean())), 2),
                  median_abs_after=round(float(np.median(np.abs(r1))), 2), cam=np.round(cam, 3).tolist(), h=round(float(h), 3), f=round(float(K[0, 0]), 1),
                  rot_corr_deg=np.round(np.degrees(sol.x[3:6]), 2).tolist())
    print(v, out[v])
json.dump(cams, open(D + 'cams.json', 'w'), indent=1); json.dump(out, open(D + 'refine_report.json', 'w'), indent=1)
