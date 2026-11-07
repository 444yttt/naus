from pathlib import Path
import numpy as np,json
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parent;O=R/'out_Y';shot='p13';c=json.loads((R/f'out_X/{shot}_camera.json').read_text());r=next(v for v in json.loads((R/'out_X/camera_fit_X.json').read_text()) if v['shot']==shot);p=np.array(r['controls_world']);uv=np.array(r['controls_observed_native_px']);rv=Rotation.from_matrix(c['R']).as_rotvec();t=np.array([.9375,2.58522727]);t/=np.linalg.norm(t);start=np.r_[rv,c['C'],np.log(c['f']),(np.array(c['principal_point_native_px'])-[c['W']/2,c['H']/2])/c['W'],0.]
def project(x):
 P=p.copy();P[7,:2]+=t*x[9];q=(P-x[3:6])@Rotation.from_rotvec(x[:3]).as_matrix().T;return q[:,:2]/q[:,2:]*np.exp(x[6])+[c['W']/2,c['H']/2]+x[7:9]*c['W']
lo=np.r_[rv-.15,np.array(c['C'])-1,np.log(c['f']*.7),-.05,-.05,-.5];hi=np.r_[rv+.15,np.array(c['C'])+1,np.log(c['f']*1.3),.05,.05,.5]
fit=least_squares(lambda x:(project(x)-uv).ravel(),start,bounds=(lo,hi),max_nfev=5000,xtol=1e-12,ftol=1e-12,gtol=1e-12);err=np.linalg.norm(project(fit.x)-uv,axis=1);out={'shot':shot,'rms':float(np.sqrt((err**2).mean())),'max':float(err.max()),'corner_distance_adjustment_m':float(fit.x[9]),'original_far_corner':p[7].tolist(),'refined_far_corner':(p[7]+np.r_[t*fit.x[9],0]).tolist(),'parameters':fit.x.tolist(),'predicted':project(fit.x).tolist(),'residuals_px':err.tolist(),'status':'DIAGNOSTIC: one shared proxy far-corner parameter slides along existing island long edge. All 11 observations retained. Near-end interface, window geometry and furniture unchanged. Not yet adopted.'};(O/'camera_island_corner_diagnostic.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
