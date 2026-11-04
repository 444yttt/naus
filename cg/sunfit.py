import numpy as np, cv2
from geo import *
ppm = 50
xs = np.arange(0.8, -4.6, -1 / ppm); ys = np.arange(-4.7, 0.75, 1 / ppm); X, Y = np.meshgrid(xs, ys)
P = np.c_[X.ravel(), Y.ravel(), np.zeros(X.size)]
lum = {}; valid = {}
for v in ('v1', 'v2'):
    uv = proj(v, P).astype(np.float32).reshape(X.shape + (2,))
    g = cv2.cvtColor(cv2.imread(S + v + '.jpg'), cv2.COLOR_BGR2GRAY).astype(np.float32)
    t = cv2.remap(g, uv[..., 0], uv[..., 1], cv2.INTER_LINEAR, borderValue=-1)
    ok = (t >= 0) & ~((X > 0) & (Y > 0))                    # inside the photo, not the pier
    t = cv2.GaussianBlur(np.where(ok, t, 0), (0, 0), 1)
    lum[v] = t; valid[v] = ok & (Y < 0.6) & (X > -4.5)
MUL = [-1.18, -2.355, -3.53]
def lit(az_deg, el_deg, mw=0.06, head=2.40, sill=0.07, dx=0.0):
    az = np.radians(az_deg)
    sx, sy = np.sin(az), np.cos(az)                         # horizontal direction toward the sun (sy > 0: toward W1)
    t = (0.87 - Y) / sy                                     # horizontal distance to the W1 plane
    hx = X + sx * t + dx; hz = np.tan(np.radians(el_deg)) * t
    ok = (hx < 0) & (hx > -4.69) & (hz > sill) & (hz < head)
    for m in MUL: ok &= np.abs(hx - m) > mw / 2
    return ok
def score(*a):
    s = 0
    for v in lum:
        m = valid[v]; p = lit(*a)[m].astype(float); l = lum[v][m]
        s += np.corrcoef(p, l)[0, 1]
    return s / 2
best = max(((score(az, el), az, el) for az in np.arange(-40, 0.1, 1) for el in np.arange(14, 40, 1)))
print('coarse', best)
_, az0, el0 = best
best = max(((score(az, el), az, el) for az in np.arange(az0 - 1.5, az0 + 1.51, 0.25) for el in np.arange(el0 - 1.5, el0 + 1.51, 0.25)))
print('fine', best)
_, az, el = best
for mw in (0.04, 0.06, 0.08, 0.10, 0.12): print('mullion', mw, round(score(az, el, mw), 4))
for dx in (-0.1, -0.05, 0, 0.05, 0.1): print('dx', dx, round(score(az, el, 0.06, 2.4, 0.07, dx), 4))
vis = []
for v in lum:
    im = cv2.cvtColor(np.clip(lum[v], 0, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
    c, _ = cv2.findContours(lit(az, el).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE); cv2.drawContours(im, c, -1, (255, 0, 255), 1)
    vis.append(cv2.resize(im, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST))
cv2.imwrite(S + 'sunfit.png', np.hstack(vis))
best2 = max(((score(a, e, 0.05, h), a, e, h) for a in np.arange(az - 1, az + 1.01, 0.5) for e in np.arange(el - 3, el + 1.01, 0.5) for h in np.arange(2.3, 2.75, 0.05)))
print('with head', best2)
