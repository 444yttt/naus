from pathlib import Path
import cv2,json,numpy as np
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_S';report={}
for s in ['u1','u2','p09','p01','p13']:
 im=cv2.imread(str(O/f'{s}_preview_foreground.png'),-1);c=json.loads((O/f'{s}_camera.json').read_text())
 mask=cv2.imread(str(O/f'{s}_effect_mask.png'),0) if (O/f'{s}_effect_mask.png').exists() else (im[:,:,3]>0).astype('uint8')
 xx,yy,ww,hh=cv2.boundingRect(mask);sx=c['W']/im.shape[1];sy=c['H']/im.shape[0];pad=128
 report[s]=[max(0,int(xx*sx)-pad),max(0,int(yy*sy)-pad),min(c['W'],int(np.ceil((xx+ww)*sx))+pad),min(c['H'],int(np.ceil((yy+hh)*sy))+pad)]
(O/'foreground_bounds.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(report)
