"""Trace real architectural edges to quantify residual curvature before any warp."""
from pathlib import Path
import cv2,json,numpy as np,sys
from scipy.optimize import minimize_scalar
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_S'
shot=sys.argv[1] if len(sys.argv)>1 else 'u1'
c=json.loads((O/f'{shot}_camera.json').read_text());im=cv2.imread(str(R/f'images/photos/{shot}.jpg'));W,H=c['W'],c['H'];s=W/(1824 if shot=='u2' else 1368)
gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(float)
dx=cv2.Sobel(gray,cv2.CV_64F,1,0,ksize=3);dy=cv2.Sobel(gray,cv2.CV_64F,0,1,ksize=3)
segments={
'u1':[[[305,750],[314,1014]],[[822,750],[822,1000]],[[1080,640],[1080,1140]],[[340,1028],[790,1017]],[[400,731],[790,731]]],
'u2':[[[187,400],[193,870]],[[750,400],[751,850]],[[1250,430],[1244,850]],[[800,397],[1190,408]],[[800,873],[1190,860]]],
'p09':[[[203,790],[210,1230]],[[1240,815],[1240,1090]],[[1000,818],[1200,790]],[[1000,1078],[1200,1110]],[[250,1230],[700,1090]]],
'p01':[[[620,690],[620,1260]],[[1275,690],[1275,1250]],[[700,678],[1200,678]],[[700,1280],[1200,1280]]],
'p13':[[[570,760],[570,1020]],[[631,1180],[631,1600]],[[350,1100],[350,1410]],[[1130,1020],[1130,1130]]]
}[shot]
traces=[];reports=[]
for a,b in segments:
 a=np.array(a)*s;b=np.array(b)*s;d=b-a;d/=np.linalg.norm(d);normal=np.array([-d[1],d[0]])
 pts=[]
 for t in np.linspace(.02,.98,80):
  p=a*(1-t)+b*t;off=np.linspace(-5*s,5*s,81);q=p+off[:,None]*normal
  xx=np.clip(np.rint(q[:,0]).astype(int),0,W-1);yy=np.clip(np.rint(q[:,1]).astype(int),0,H-1)
  strength=np.abs(dx[yy,xx]*normal[0]+dy[yy,xx]*normal[1])
  j=np.argmax(strength)
  if strength[j]>60 and 2<j<78:pts.append(q[j])
 pts=np.array(pts)
 if len(pts)<20:continue
 # Straightness residual after robustly excluding edge crossings.
 ctr=pts.mean(0);_,_,v=np.linalg.svd(pts-ctr);dist=(pts-ctr)@v[-1];good=np.abs(dist-np.median(dist))<3*s
 pts=pts[good];ctr=pts.mean(0);_,_,v=np.linalg.svd(pts-ctr);dist=(pts-ctr)@v[-1]
 traces.append(pts);reports.append({'endpoints_at_1368px':[list(a/s),list(b/s)],'n':len(pts),'rms_px':float(np.sqrt(np.mean(dist**2))),'max_abs_px':float(np.max(np.abs(dist)))})
 for p in pts:cv2.circle(im,tuple(np.rint(p).astype(int)),4,(0,255,255),-1)
def score(k):
 vals=[]
 for pts in traces:
  q=(pts-[W/2,H/2])/c['f'];r=(q*q).sum(1)
  u=q/(1+k*r[:,None]);u*=c['f'];u-=u.mean(0);_,_,v=np.linalg.svd(u);vals.extend((u@v[-1]).tolist())
 return np.mean(np.array(vals)**2)
fit=minimize_scalar(score,bounds=(-.04,.04),method='bounded');before=float(np.sqrt(score(0)));after=float(np.sqrt(fit.fun))
# Sparse architectural edges and unknown electronic correction: avoid unsupported peripheral warp.
report={'shot':shot,'edge_traces':reports,'straightness_rms_before_px':before,'candidate_k1':float(fit.x),'candidate_straightness_rms_px':after,'applied_k1':0,'applied_k2':0,'decision':'No extra warp applied in first iteration. Sparse straight-edge traces constrain local curvature only; residuals and candidate are recorded, not assumed to be a full lens calibration.'}
(O/f'{shot}_lens_check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
cv2.putText(im,f"Straight-edge trace RMS {before:.2f}px; extra warp withheld pending validation",(70,110),cv2.FONT_HERSHEY_SIMPLEX,2,(0,255,255),4)
cv2.imwrite(str(O/f'{shot}_lens_check.jpg'),im,[cv2.IMWRITE_JPEG_QUALITY,94])
print(json.dumps(report,indent=2))
