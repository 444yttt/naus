from pathlib import Path
import numpy as np,json,math
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parent;O=R/'out_Y';O.mkdir(exist_ok=True)
data=json.loads((R/'out_X/camera_fit_X.json').read_text());results=[]
for shot in ['u2','p13']:
 c=json.loads((R/f'out_X/{shot}_camera.json').read_text());d=next(v for v in data if v['shot']==shot);p=np.array(d['controls_world']);uv=np.array(d['controls_observed_native_px']);rv=Rotation.from_matrix(c['R']).as_rotvec();pp=np.array(c['principal_point_native_px']);start=np.r_[rv,c['C'],math.log(c['f']),(pp-[c['W']/2,c['H']/2])/c['W'],0,0,0,0]
 for mode,active in [('pinhole',9),('radial1',10),('radial2',11),('brown',13)]:
  def project(x):
   z=np.zeros(13);z[:len(x)]=x;q=(p-z[3:6])@Rotation.from_rotvec(z[:3]).as_matrix().T;a=q[:,:2]/q[:,2:];r2=(a*a).sum(1);f=1+z[9]*r2+z[10]*r2*r2
   xx=a[:,0]*f+2*z[11]*a[:,0]*a[:,1]+z[12]*(r2+2*a[:,0]**2);yy=a[:,1]*f+z[11]*(r2+2*a[:,1]**2)+2*z[12]*a[:,0]*a[:,1]
   return np.stack([xx,yy],1)*np.exp(z[6])+[c['W']/2,c['H']/2]+z[7:9]*c['W']
  lo=np.r_[rv-.15,np.array(c['C'])-1.,math.log(c['f']*.7),-.05,-.05,-.12,-.12,-.025,-.025][:active];hi=np.r_[rv+.15,np.array(c['C'])+1.,math.log(c['f']*1.3),.05,.05,.12,.12,.025,.025][:active]
  x0=np.clip(start[:active],lo+1e-8,hi-1e-8);fit=least_squares(lambda x:(project(x)-uv).ravel(),x0,bounds=(lo,hi),max_nfev=6000,ftol=1e-12,xtol=1e-12,gtol=1e-12);err=np.linalg.norm(project(fit.x)-uv,axis=1)
  row={'shot':shot,'model':mode,'rms':float(np.sqrt((err**2).mean())),'max':float(err.max()),'parameters':fit.x.tolist(),'residuals':err.tolist()};results.append(row);print(shot,mode,row['rms'],row['max'],fit.x[9:],flush=True)
(O/'camera_lens_diagnostic.json').write_text(json.dumps(results,indent=2))
