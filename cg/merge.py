"""Composite: photo * shadow-catcher + furniture (premultiplied), in linear light; optionally the furniture's
reflection in the polished floor (render of the mirrored scene), weighted by the tile's Fresnel reflectance.
usage: merge.py photo.jpg combined.npy catcher.npy out.jpg [refl.npy view]"""
import sys, os, numpy as np, cv2
ph, cb, ct, out = sys.argv[1:5]
comb = np.load(cb); cat = np.load(ct)[..., :3]
H, W = comb.shape[:2]; img = cv2.imread(ph)[..., ::-1] / 255.0
img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA) if img.shape[:2] != (H, W) else img
lin = lambda x: np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
enc = lambda x: np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(np.clip(x, 0, None), 1 / 2.4) - 0.055)
P = lin(img); rgb, a = comb[..., :3], comb[..., 3:4]
cat = np.nan_to_num(np.clip(cat, 0, 1.0), nan=1.0)   # furniture only takes light away
if os.environ.get('AO'):                                       # contact occlusion of the furniture on the floor
    ao = np.nan_to_num(np.clip(np.load(os.environ['AO'])[..., :3].mean(2), 0, 1), nan=1.0)
    if ao.shape != (H, W): ao = cv2.resize(ao, (W, H), interpolation=cv2.INTER_LINEAR)
    cat = cat * (1 - float(os.environ.get('AO_K', 0.6)) * (1 - ao))[..., None]
bgd = P * cat
if len(sys.argv) > 6:
    from geo import cam
    ref = np.load(sys.argv[5]); view = sys.argv[6]
    if ref.shape[:2] != (H, W): ref = cv2.resize(ref, (W, H), interpolation=cv2.INTER_LINEAR)
    K, R, C = cam(view); s = W / 1932.0
    # floor pixels: rays that hit z = 0 inside the room (not the pier, not through the glass)
    u, v = np.meshgrid((np.arange(W) + 0.5) / s, (np.arange(H) + 0.5) / s)
    d = np.einsum('ij,hwj->hwi', R.T @ np.linalg.inv(K), np.dstack([u, v, np.ones_like(u)]))
    d /= np.linalg.norm(d, axis=-1, keepdims=True)
    tz = -C[2] / np.where(d[..., 2] < -1e-6, d[..., 2], -1e-6); X = C[0] + tz * d[..., 0]; Y = C[1] + tz * d[..., 1]
    floor = (d[..., 2] < 0) & (X > -4.69) & (X < 0.89) & (Y > -4.83) & (Y < 0.87) & ~((X > 0) & (Y > 0))
    if view == 'v3':                                              # the kitchen island and wall stand in front of the floor
        for x0, x1, y0, y1, z1 in ((-3.33, -0.9, -5.21, -4.24, 0.88), (-1.68, -0.9, -6.3, -4.24, 0.88), (-0.9, 0.89, -6.5, -4.40, 2.65)):
            with np.errstate(divide='ignore', invalid='ignore'):
                for ax, a0, a1 in ((0, x0, x1), (1, y0, y1), (2, 0.0, z1)):
                    for pl in (a0, a1):
                        t = (pl - C[ax]) / d[..., ax]
                        Pt = C[None, None, :] + t[..., None] * d
                        o = [i for i in range(3) if i != ax]; lim = ((x0, x1), (y0, y1), (0.0, z1))
                        inside = (t > 0) & (t < tz)
                        for i in o: inside &= (Pt[..., i] >= lim[i][0]) & (Pt[..., i] <= lim[i][1])
                        floor &= ~inside
    cos = np.clip(-d[..., 2], 0, 1)
    F = np.minimum(1.5 * (0.06 + (1 - 0.06) * (1 - cos) ** 5), 0.6)  # Schlick for glazed tile plus its polish coat; the
    k = (F * floor)[..., None]                                       # photo shows the window frames clearly in the floor
    blur = lambda x: cv2.GaussianBlur(x, (0, 0), max(0.6, 2.0 * s))
    rr, ra = blur(np.ascontiguousarray(ref[..., :3])), blur(np.ascontiguousarray(ref[..., 3]))[..., None]
    bgd = bgd * (1 - k * ra) + k * rr                              # the mirrored furniture replaces what the tile reflected there
o = rgb + (1 - a) * bgd
import os
mf = os.path.join(os.path.dirname(ph), os.path.basename(ph).split('.')[0] + '_matte.png')
if os.path.exists(mf):                                        # real foreground objects cut from the photo (e.g. the tap)
    mt = cv2.imread(mf, 0); mt = cv2.resize(mt, (W, H), interpolation=cv2.INTER_AREA) if mt.shape != (H, W) else mt
    mt = cv2.GaussianBlur(mt.astype(np.float32) / 255, (0, 0), 0.8)[..., None]
    o = o * (1 - mt) + P * mt
if len(sys.argv) > 7:                                          # a top layer that stands in front of the photo matte
    top = np.load(sys.argv[7])
    if len(sys.argv) > 8:                                      # the top layer's shadows on the worktop
        tc = np.nan_to_num(np.clip(np.load(sys.argv[8])[..., :3], 0, 1.0), nan=1.0); o = o * tc
    o = top[..., :3] + (1 - top[..., 3:4]) * o
cv2.imwrite(out, (np.clip(enc(o), 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 93])
