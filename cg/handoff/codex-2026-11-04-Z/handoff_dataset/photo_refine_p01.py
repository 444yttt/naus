from pathlib import Path
import cv2,json,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_S';c=json.loads((O/'p01_camera.json').read_text())
im=cv2.imread(str(R/'images/photos/p01.jpg'));scale=1600/c['W'];im=cv2.resize(im,(1600,round(c['H']*scale)));gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
ls=cv2.createLineSegmentDetector().detect(gray)[0].reshape(-1,4)/scale
rot=np.array(c['R']);vp=rot[:,0];vp=vp[:2]/vp[2]*c['f']+[c['W']/2,c['H']/2]
floor=[];vertical=[]
for line in ls:
 a,b=line[:2],line[2:];d=b-a;le=np.linalg.norm(d);m=(a+b)/2
 if le<150:continue
 d/=le
 if m[1]>1295*c['W']/1368:
  t=vp-m;t/=np.linalg.norm(t)
  if abs(d[0]*t[1]-d[1]*t[0])<np.sin(np.radians(5)):floor.append(line)
 elif le>350 and abs(d[0])<.025 and m[1]>c['H']*.35:vertical.append(line)
rv=Rotation.from_matrix(rot).as_rotvec();x0=np.r_[rv,np.log(c['f'])]
train=floor[::2];test=floor[1::2]
def lineerr(x,lines,axis):
 rr=Rotation.from_rotvec(x[:3]).as_matrix();v=rr[:,axis];hom=np.r_[v[:2]*np.exp(x[3])+np.array([c['W']/2,c['H']/2])*v[2],v[2]]
 out=[]
 for ln in lines:
  a,b=ln[:2],ln[2:];m=(a+b)/2;vec=hom[:2]-m*hom[2];vec/=np.linalg.norm(vec);d=b-a
  out.append(.5*(d[0]*vec[1]-d[1]*vec[0]))
 return np.array(out)
def res(x):return np.r_[lineerr(x,train,0)/2,lineerr(x,vertical,2)/2,(x[:3]-rv)/np.radians(1),(x[3]-x0[3])/.05]
fit=least_squares(res,x0,loss='soft_l1',f_scale=2,max_nfev=500)
c['R']=Rotation.from_rotvec(fit.x[:3]).as_matrix().tolist();c['f']=float(np.exp(fit.x[3]))
a=c['anchor'];uv=np.array(a['pixel']);ray=np.array(c['R']).T@np.r_[(uv-[c['W']/2,c['H']/2])/c['f'],1]
c['C']=(np.array(a['world'])+c['C'][2]/ray[2]*ray).tolist()
c['floor_orientation_refinement']={'train_count':len(train),'holdout_count':len(test),'vertical_count':len(vertical),'holdout_endpoint_rms_px':float(np.sqrt(np.mean(lineerr(fit.x,test,0)**2))),'before_holdout_endpoint_rms_px':float(np.sqrt(np.mean(lineerr(x0,test,0)**2))),'scope':'orientation only; inherited absolute scale and cross-view anchor remain inferred'}
(O/'p01_camera.json').write_text(json.dumps(c,indent=2),encoding='utf8');print(json.dumps(c['floor_orientation_refinement'],indent=2))
