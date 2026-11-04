"""Diagnostic bundle: one shared island width, near-end plane fixed.
Raster-plan width is approximate; all photo corners retained. No furniture move.
"""
from pathlib import Path
import numpy as np,json
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parent;O=R/'out_Y';data=[];base=[];lo=[];hi=[];t=np.array([35.,-12.]);t/=np.linalg.norm(t)
rows=json.loads((R/'out_X/camera_fit_X.json').read_text());A=np.array([3.8352272727272725,6.90340909090909]);B=np.array([4.829545454545454,6.5625]);oldwidth=float(np.linalg.norm(B-A))
for shot in ['u2','p13']:
 c=json.loads((R/f'out_X/{shot}_camera.json').read_text());r=next(x for x in rows if x['shot']==shot);p=np.array(r['controls_world'])
 if shot=='u2':m=json.loads((O/'native_edge_camera_u2.json').read_text())[0];uv=np.array(m['observations_refined']);sign={7:-1,8:1,9:-1,10:1}
 else:m=json.loads((O/'native_edge_camera_p13.json').read_text());uv=np.array(m['observations_native_edge_refined']);sign={3:-1,4:1,5:1,6:1,7:-1,8:-1,9:1,10:1}
 rv=Rotation.from_matrix(c['R']).as_rotvec();base.extend(np.r_[rv,c['C'],np.log(c['f']),(np.array(c['principal_point_native_px'])-[c['W']/2,c['H']/2])/c['W']]);lo.extend(np.r_[rv-.15,np.array(c['C'])-1,np.log(c['f']*.7),-.05,-.05]);hi.extend(np.r_[rv+.15,np.array(c['C'])+1,np.log(c['f']*1.3),.05,.05]);data.append((shot,c,p,uv,sign))
base=np.r_[base,0.];lo=np.r_[lo,-.05];hi=np.r_[hi,.10]
def project(x,i):
 _,c,p,uv,sign=data[i];p=p.copy()
 for k,v in sign.items():p[k,:2]+=v*t*x[-1]/2
 z=x[i*9:i*9+9];q=(p-z[3:6])@Rotation.from_rotvec(z[:3]).as_matrix().T;return q[:,:2]/q[:,2:]*np.exp(z[6])+[c['W']/2,c['H']/2]+z[7:9]*c['W']
fit=least_squares(lambda x:np.concatenate([(project(x,i)-uv).ravel() for i,(_,c,p,uv,s) in enumerate(data)]),base,bounds=(lo,hi),max_nfev=6000,xtol=1e-12,ftol=1e-12,gtol=1e-12)
out={'original_island_width_m':oldwidth,'refined_width_m':oldwidth+float(fit.x[-1]),'delta_width_m':float(fit.x[-1]),'near_end_midpoint_and_plane_unchanged':True,'observations_removed':0,'status':'DIAGNOSTIC ONLY. Shared physical width estimated across two views, no per-point correction. Not adopted until independent structural checks.','cameras':[]}
for i,(shot,c,p,uv,sign) in enumerate(data):
 er=np.linalg.norm(project(fit.x,i)-uv,axis=1);out['cameras'].append({'shot':shot,'rms':float(np.sqrt(np.mean(er**2))),'max':float(er.max()),'parameters':fit.x[i*9:i*9+9].tolist(),'residuals':er.tolist()})
(O/'camera_shared_island_width_diagnostic.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
