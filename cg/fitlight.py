"""Fit sun and sky intensities (per channel) so the empty-room renders (sun=1, sky=1) reproduce the photo's floor.
usage: fitlight.py photo.jpg sun.npy amb.npy out_light.json check.png"""
import os, sys, json, numpy as np
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'; import cv2
ph, se, ae, out, chk = sys.argv[1:6]
sun = np.load(se)[..., [2, 1, 0, 3]]; amb = np.load(ae)[..., [2, 1, 0, 3]]          # stored RGBA -> BGRA like the rest
H, W = sun.shape[:2]; img = cv2.resize(cv2.imread(ph), (W, H), interpolation=cv2.INTER_AREA)
lin = lambda x: np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
P = lin(img[..., ::-1] / 255.0); Su = sun[..., 2::-1]; Am = amb[..., 2::-1]; alpha = sun[..., 3]
floor = alpha > 0.99
floor[: int(H * 0.62)] = False                     # floor area only (below the window sill in these views)
# the polished tile mirrors the dark back of the room near the camera, which a diffuse floor cannot show; the furniture
# stands in the middle band, so fit there
floor[int(H * 0.80):] = False
# lit/unlit agreement between the sun render and the photo
lum = lambda x: x @ np.array([.2126, .7152, .0722])
ls = lum(Su); lp = lum(P)
lit_r = ls > 0.5 * np.percentile(ls[floor], 95)
thr = np.percentile(lp[floor], 50); lit_p = lp > thr * 1.0
f = floor & np.isfinite(ls)
inter = (lit_r & lit_p & f).sum(); union = ((lit_r | lit_p) & f).sum()
res = {}
# Two reference areas at the furniture's distance from the windows: sunlit tile and tile in the pier's shadow next
# to the patch (fractions of the image, per view). Solve sun and sky per channel from them.
REF = json.loads(os.environ.get('FIT_REF', '{"lit": [0.668, 0.715, 0.21, 0.31], "shade": [0.70, 0.81, 0.02, 0.155]}'))
box = lambda r: (slice(int(r[0] * H), int(r[1] * H)), slice(int(r[2] * W), int(r[3] * W)))
k = []
for c in range(3):
    A_ = np.array([[np.median(Su[box(REF[n])][..., c]), np.median(Am[box(REF[n])][..., c])] for n in ('lit', 'shade')])
    y_ = np.array([np.median(P[box(REF[n])][..., c]) for n in ('lit', 'shade')])
    k.append(np.linalg.solve(A_, y_))
k = np.array(k); res['ref'] = REF
fit = Su * k[:, 0] + Am * k[:, 1]
err = np.abs(lum(fit) - lp)[f]
# the calibration renders already carry the floor albedo, so k are the light multipliers themselves
light = dict(sun=list(k[:, 0]), sky=list(k[:, 1]), **res,
             lit_IoU=float(inter / union), median_abs_lum_err=float(np.median(err)), photo_floor_lum=float(np.median(lp[f])))
json.dump(light, open(out, 'w'), indent=1); print(json.dumps(light, indent=1))
enc = lambda x: (np.clip(np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(np.clip(x, 0, None), 1 / 2.4) - 0.055), 0, 1) * 255).astype(np.uint8)
vis = np.hstack([img, enc(fit)[..., ::-1] * f[..., None] + img * (~f[..., None]),
                 np.dstack([lit_p & f, lit_r & f, np.zeros_like(f)]).astype(np.uint8) * 255])
cv2.imwrite(chk, vis)
