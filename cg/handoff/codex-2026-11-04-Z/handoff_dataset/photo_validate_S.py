"""Independent image-line diagnostics; does not re-fit the camera."""
from pathlib import Path
import json,cv2,numpy as np
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_S'
polys={
'u1':(1368,[[0,1090],[314,1035],[820,1023],[1368,1380],[1368,1824],[0,1824]]),
'u2':(1824,[[0,900],[1480,870],[1480,1100],[1824,1240],[1824,1368],[0,1368]]),
'p09':(1368,[[0,1300],[847,1055],[1368,1150],[1368,1824],[0,1824]]),
'p01':(1368,[[0,1295],[1368,1295],[1368,1824],[0,1824]]),
'p13':(1368,[[0,1360],[330,1260],[340,1440],[630,1660],[970,1290],[1120,1180],[1368,1420],[1368,1824],[0,1824]])}
reports=[]
for shot,(ref,poly) in polys.items():
 c=json.loads((O/f'{shot}_camera.json').read_text());im=cv2.imread(str(R/f'images/photos/{shot}.jpg'));W,H=c['W'],c['H'];scale=1600/W
 small=cv2.resize(im,(1600,round(H*scale)));gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
 mask=np.zeros(gray.shape,'uint8');cv2.fillPoly(mask,[np.rint(np.array(poly)*1600/ref).astype('int32')],255)
 lsd=cv2.createLineSegmentDetector();ls=lsd.detect(gray)[0]
 rot=np.array(c['R']);vp=rot[:,0];vp=vp[:2]/vp[2]*c['f']+[W/2,H/2];vp*=scale
 errs=[];angles=[];used=[]
 if ls is not None:
  for line in ls.reshape(-1,4):
   a,b=line[:2],line[2:];m=(a+b)/2;length=np.linalg.norm(b-a)
   if length<65:continue
   ix=np.rint(np.array([a,m,b])).astype(int)
   if np.any(ix[:,0]<0) or np.any(ix[:,0]>=1600) or np.any(ix[:,1]<0) or np.any(ix[:,1]>=gray.shape[0]):continue
   if not np.all(mask[ix[:,1],ix[:,0]]):continue
   d=(b-a)/length;t=(vp-m);t/=np.linalg.norm(t);sine=abs(d[0]*t[1]-d[1]*t[0]);angle=np.degrees(np.arcsin(min(1,sine)))
   # Avoid treating cross-grain/end joints as the X-axis seam family.
   if angle>5:continue
   err=.5*length*sine/scale;errs.append(err);angles.append(angle);used.append((a,b))
   aa=m-t*length*.55;bb=m+t*length*.55
   cv2.line(small,tuple(a.astype(int)),tuple(b.astype(int)),(255,255,0),2)
   cv2.line(small,tuple(aa.astype(int)),tuple(bb.astype(int)),(0,255,0),1)
 rep={'shot':shot,'floor_line_count':len(errs),'endpoint_direction_rms_px':float(np.sqrt(np.mean(np.array(errs)**2))) if errs else None,'median_angle_error_deg':float(np.median(angles)) if angles else None,'max_selected_angle_deg':5,'interpretation':'LSD floor-region long lines, selected within5deg of X-direction. Grain can be included. Independent orientation diagnostic, not absolute position error or surveyed calibration.'}
 reports.append(rep)
 cv2.putText(small,f"{shot}: floor line n={len(errs)}, orientation endpoint RMS {rep['endpoint_direction_rms_px'] or 0:.1f}px",(30,50),cv2.FONT_HERSHEY_SIMPLEX,.85,(0,255,255),2)
 # Overlay floor contact footprints with the same metric scene coordinates.
 world=np.array([[5.2,.35,0],[8.7,.35,0],[8.7,4.35,0],[5.2,4.35,0]],float)
 cam=(world-c['C'])@rot.T
 if np.all(cam[:,2]>.01):
  q=(cam[:,:2]/cam[:,2:]*c['f']+[W/2,H/2])*scale
  for a,b in zip(q,np.roll(q,-1,axis=0)):
   if np.max(abs(np.r_[a,b]))<1e5:cv2.line(small,tuple(a.astype(int)),tuple(b.astype(int)),(0,165,255),2)
 cv2.imwrite(str(O/f'{shot}_floor_check.jpg'),small,[cv2.IMWRITE_JPEG_QUALITY,94])
(O/'floor_validation.json').write_text(json.dumps(reports,indent=2),encoding='utf8');print(json.dumps(reports,indent=2))
