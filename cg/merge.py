"""Composite: photo * shadow-catcher + furniture (premultiplied), in linear light.
usage: merge.py photo.jpg combined.npy catcher.npy out.jpg"""
import sys, numpy as np, cv2
ph, cb, ct, out = sys.argv[1:5]
comb = np.load(cb); cat = np.load(ct)[..., :3]
H, W = comb.shape[:2]; img = cv2.imread(ph)[..., ::-1] / 255.0
img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA) if img.shape[:2] != (H, W) else img
lin = lambda x: np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
enc = lambda x: np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(np.clip(x, 0, None), 1 / 2.4) - 0.055)
P = lin(img); rgb, a = comb[..., :3], comb[..., 3:4]
cat = np.nan_to_num(np.clip(cat, 0, 1.2), nan=1.0)
o = rgb + (1 - a) * P * cat
cv2.imwrite(out, (np.clip(enc(o), 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 93])
