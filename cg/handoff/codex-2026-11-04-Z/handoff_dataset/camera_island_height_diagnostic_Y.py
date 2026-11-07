from pathlib import Path
import numpy as np,json
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parent;O=R/'out_Y';allrows=json.loads((R/'out_X/camera_fit_X.json').read_text());data=[];base=[];lo=[];hi=[]
for shot in ['u2','p13']:
 c=json.loads((R/f'out_X/{shot}_camera.json').read_text());r=next(v for v in allrows if v['shot']==shot);rv=Rotation.from_matrix(c['R']).as_rotvec();x=np.r_[rv,c['C'],np.log(c['f']),(np.array(c['principal_point_native_px'])-[c['W']/2,c['H']/2])/c['W']];base.extend(x);lo.extend(np.r_[rv-.15,np.array(c['C'])-1,np.log(c['f']*.7),-.05,-.05]);hi.extend(np.r_[rv+.15,np.array(c['C'])+1,np.log(c['f']*1.3),.05,.05]);data.append((shot,c,r))
base=np.r_[base,0.91];lo=np.r_[lo,.85];hi=np.r_[hi,.95]
def project(x,i):
 _,c,r=data[i];p=np.array(r['controls_world']);p[abs(p[:,2]-.91)<.001,2]=x[-1];z=x[i*9:i*9+9];q=(p-z[3:6])@Rotation.from_rotvec(z[:3]).as_matrix().T;return q[:,:2]/q[:,2:]*np.exp(z[6])+[c['W']/2,c['H']/2]+z[7:9]*c['W']
fit=least_squares(lambda x:np.concatenate([(project(x,i)-r['controls_observed_native_px']).ravel() for i,(_,c,r) in enumerate(data)]),base,bounds=(lo,hi),max_nfev=6000,xtol=1e-12,ftol=1e-12,gtol=1e-12)
results=[]
for i,(shot,c,r) in enumerate(data):
 err=np.linalg.norm(project(fit.x,i)-r['controls_observed_native_px'],axis=1);results.append({'shot':shot,'rms_px':float(np.sqrt((err**2).mean())),'max_px':float(err.max()),'island_height_m':float(fit.x[-1]),'parameters':fit.x[i*9:i*9+9].tolist(),'status':'DIAGNOSTIC only. Shared island height is unmeasured; original 0.91m was assumed. Observations/footprints/furniture unchanged.'})
(O/'camera_island_height_diagnostic.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
