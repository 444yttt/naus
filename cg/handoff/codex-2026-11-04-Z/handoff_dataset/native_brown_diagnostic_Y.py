from pathlib import Path
import numpy as np,json
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parent;O=R/'out_Y';m=json.loads((O/'native_edge_camera_p13.json').read_text());P=np.array(m['world_controls_unchanged']);uv=np.array(m['observations_native_edge_refined']);c=json.loads((R/'out_X/p13_camera.json').read_text());base=np.r_[m['parameters'],np.zeros(6)];rv=base[:3];results=[]
for label,active in [('brown',13),('general_brown',15)]:
 def project(x):
  z=np.zeros(15);z[:len(x)]=x;q=(P-z[3:6])@Rotation.from_rotvec(z[:3]).as_matrix().T;a=q[:,:2]/q[:,2:];r2=(a*a).sum(1);rad=1+z[9]*r2+z[10]*r2*r2;xx=a[:,0]*rad+2*z[11]*a[:,0]*a[:,1]+z[12]*(r2+2*a[:,0]**2);yy=a[:,1]*rad+z[11]*(r2+2*a[:,1]**2)+2*z[12]*a[:,0]*a[:,1];return np.stack([xx+z[14]*yy,yy*np.exp(z[13])],1)*np.exp(z[6])+[c['W']/2,c['H']/2]+z[7:9]*c['W']
 lo=np.r_[rv-.1,base[3:6]-.6,np.log(np.exp(base[6])*.8),-.025,-.025,-.1,-.1,-.01,-.01,-.025,-.025][:active];hi=np.r_[rv+.1,base[3:6]+.6,np.log(np.exp(base[6])*1.2),.025,.025,.1,.1,.01,.01,.025,.025][:active]
 fit=least_squares(lambda x:(project(x)-uv).ravel(),np.clip(base[:active],lo+1e-8,hi-1e-8),bounds=(lo,hi),max_nfev=5000,xtol=1e-12,ftol=1e-12,gtol=1e-12);err=np.linalg.norm(project(fit.x)-uv,axis=1);results.append({'model':label,'rms':float(np.sqrt((err**2).mean())),'max':float(err.max()),'parameters':fit.x.tolist(),'status':'diagnostic only; independent straight-edge validation required, no production application'})
(O/'native_brown_diagnostic.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
