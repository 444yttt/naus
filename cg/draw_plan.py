"""Draw a layout option from layout.json onto the floor-plan image (and the camera positions)."""
import json, math, sys
from PIL import Image, ImageDraw, ImageFont
L = json.load(open(sys.argv[1])); plan = sys.argv[2]; cams = json.load(open(sys.argv[3])); opt = sys.argv[4]; out = sys.argv[5]
s = L['plan_scale_m_per_px']; ox, oy = 167, 1298                 # column corner in plan pixels
P = lambda x, y: (ox - x / s, oy + y / s)
im = Image.open(plan).convert('RGB').crop((30, 600, 650, 1427)); dx, dy = 30, 600
im = im.resize((im.size[0] * 2, im.size[1] * 2)); k = 2
Q = lambda x, y: ((P(x, y)[0] - dx) * k, (P(x, y)[1] - dy) * k)
d = ImageDraw.Draw(im, 'RGBA'); f = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 22); fs = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 17)
STY = {'dining_table_round': ((214, 200, 180, 240), 'Androgyne Ø150'), 'dining_table': ((150, 110, 70, 230), 'ダイニング 240×100'), 'sofa': ((128, 116, 104, 235), 'Eave 86 構成2 247×86'), 'coffee_table': ((60, 50, 44, 230), 'ローテーブル'),
       'rug': ((200, 190, 170, 120), ''), 'tv_eclipse65': ((20, 20, 20, 240), 'B&O Eclipse 65'), 'speaker_beolab28': ((40, 40, 40, 240), ''),
       'lounge_chair': ((90, 60, 45, 230), 'ラウンジチェア'), 'chair': ((196, 150, 104, 235), ''), 'tv': ((25, 25, 25, 240), 'TV 65型(仮)'), 'coffee_table_round': ((150, 125, 100, 235), 'Ø60(仮)')}
def rect(x, y, w, dd, rot, fill, label='', back=False):
    a = math.radians(rot); c, sn = math.cos(a), math.sin(a)
    pts = [(x + c * u - sn * v, y + sn * u + c * v) for u, v in ((-w / 2, -dd / 2), (w / 2, -dd / 2), (w / 2, dd / 2), (-w / 2, dd / 2))]
    d.polygon([Q(*p) for p in pts], fill=fill, outline=(40, 30, 20, 255))
    if back: d.line([Q(*pts[2]), Q(*pts[3])], fill=(30, 25, 20, 255), width=6)     # back edge
    if label:
        X, Y = Q(x, y); tw = d.textlength(label, font=fs)
        d.rectangle((X - tw / 2 - 3, Y - 11, X + tw / 2 + 3, Y + 11), fill=(255, 255, 255, 200)); d.text((X - tw / 2, Y - 10), label, fill=(30, 30, 30), font=fs)
items = L['options'][opt]['items']
order = sorted(items, key=lambda it: it['type'] != 'rug')
table = next((it for it in items if it['type'].startswith('dining_table')), None)
for it in order:
    if it['type'] == 'chairs':
        tw, td = table['w'], table['d']; long_is_x = tw >= td; n = it['n_side']; L_ = max(tw, td)
        for i in range(n):
            u = -L_ / 2 + L_ * (i + .5) / n
            for side in (-1, 1):
                if long_is_x: rect(table['x'] + u, table['y'] + side * (td / 2 + .3), .5, .5, 0, STY['chair'][0])
                else: rect(table['x'] + side * (tw / 2 + .3), table['y'] + u, .5, .5, 0, STY['chair'][0])
        if it['ends']:
            for side in (-1, 1):
                if long_is_x: rect(table['x'] + side * (tw / 2 + .3), table['y'], .5, .5, 0, STY['chair'][0])
                else: rect(table['x'], table['y'] + side * (td / 2 + .3), .5, .5, 0, STY['chair'][0])
        continue
    fill, lab = STY[it['type']]
    if it['type'] == 'coffee_table_round':
        X, Y = Q(it['x'], it['y']); r = it['w'] / 2 / s * k
        d.ellipse((X - r, Y - r, X + r, Y + r), fill=fill, outline=(40, 30, 20, 255)); tw = d.textlength(lab, font=fs)
        d.rectangle((X - tw / 2 - 3, Y - 11, X + tw / 2 + 3, Y + 11), fill=(255, 255, 255, 200)); d.text((X - tw / 2, Y - 10), lab, fill=(30, 30, 30), font=fs)
        continue
    if it['type'] == 'dining_table_round':
        X, Y = Q(it['x'], it['y']); r = it['w'] / 2 / s * k
        d.ellipse((X - r - .85 / s * k, Y - r - .85 / s * k, X + r + .85 / s * k, Y + r + .85 / s * k), outline=(150, 60, 40, 255), width=2)
        d.ellipse((X - r, Y - r, X + r, Y + r), fill=fill, outline=(40, 30, 20, 255)); tw = d.textlength(lab, font=fs)
        d.rectangle((X - tw / 2 - 3, Y - 11, X + tw / 2 + 3, Y + 11), fill=(255, 255, 255, 200)); d.text((X - tw / 2, Y - 10), lab, fill=(30, 30, 30), font=fs)
        continue
    rect(it['x'], it['y'], it['w'], it['d'], it['rot'], fill, lab, back=it['type'] in ('chair', 'sofa', 'tv'))
for v, c in cams.items():
    X, Y = Q(*c['cam']); d.ellipse((X - 9, Y - 9, X + 9, Y + 9), fill=(220, 40, 40, 255)); d.text((X + 12, Y - 12), {'v1': '写真1・2', 'v2': '', 'v3': '写真3'}[v], fill=(200, 30, 30), font=fs)
d.rectangle((0, 0, im.size[0], 40), fill=(255, 255, 255, 230)); d.text((10, 8), L['options'][opt]['title'], fill=(20, 20, 20), font=f)
Xa, Ya = Q(-4.4, .55); Xb, _ = Q(-3.4, .55); d.line((Xa, Ya, Xb, Ya), fill=(0, 0, 0), width=4); d.text((Xa, Ya + 6), '1m', fill='black', font=fs)
im.save(out)
