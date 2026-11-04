from pathlib import Path
import numpy as np,json
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parent;O=R/'out_Y';data=json.loads((R/'out_X/camera_fit_X.json').read_text());results=[]
for shot in ['u2','p13']:
 c=json.loads((R/f'out_X/{shot}_camera.json').read_text());d=next(v for v in data if v['shot']==shot);p=np.array(d['controls_world']);uv=np.array(d['controls_observed_native_px']);rv=Rotation.from_matrix(c['R']).as_rotvec();start=np.r_[rv,c['C'],np.log(c['f']),(np.array(c['principal_point_native_px'])-[c['W']/2,c['H']/2])/c['W'],0,0,0,0,0,0]
 for mode,active in [('aspect',10),('aspect_skew',11),('aspect_skew_brown',15)]:
  def project(x):
   z=np.zeros(15);z[:len(x)]=x;q=(p-z[3:6])@Rotation.from_rotvec(z[:3]).as_matrix().T;a=q[:,:2]/q[:,2:];r2=(a*a).sum(1);rad=1+z[11]*r2+z[12]*r2*r2
   xx=a[:,0]*rad+2*z[13]*a[:,0]*a[:,1]+z[14]*(r2+2*a[:,0]**2);yy=a[:,1]*rad+z[13]*(r2+2*a[:,1]**2)+2*z[14]*a[:,0]*a[:,1]
   return np.stack([xx+z[10]*yy,yy*np.exp(z[9])],1)*np.exp(z[6])+[c['W']/2,c['H']/2]+z[7:9]*c['W']
  lo=np.r_[rv-.15,np.array(c['C'])-1,np.log(c['f']*.7),-.05,-.05,-.03,-.03,-.12,-.12,-.025,-.025][:active];hi=np.r_[rv+.15,np.array(c['C'])+1,np.log(c['f']*1.3),.05,.05,.03,.03,.12,.12,.025,.025][:active]
  fit=least_squares(lambda x:(project(x)-uv).ravel(),start[:active],bounds=(lo,hi),max_nfev=5000,xtol=1e-12,ftol=1e-12,gtol=1e-12);err=np.linalg.norm(project(fit.x)-uv,axis=1)
  results.append({'shot':shot,'model':mode,'rms':float(np.sqrt((err**2).mean())),'max':float(err.max()),'parameters':fit.x.tolist(),'status':'diagnostic, not applied'});print(shot,mode,results[-1]['rms'],results[-1]['max'],fit.x[9:],flush=True)
(O/'camera_intrinsic_diagnostic.json').write_text(json.dumps(results,indent=2))
