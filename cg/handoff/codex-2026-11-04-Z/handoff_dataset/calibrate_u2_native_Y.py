from pathlib import Path
import json,numpy as np,cv2
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parent;O=R/'out_Y';shot='u2'
data=json.loads((O/'u2_island_edge_segments.json').read_text());long=json.loads((O/'u2_B_top_edge_segments.json').read_text())
def tls(lines):
 v=cv2.fitLine(np.asarray(lines,dtype='float32').reshape(-1,2),cv2.DIST_L2,0,.001,.001).reshape(-1);dx,dy,x,y=v;return np.array([-dy,dx,dy*x-dx*y],dtype='float64')
def line(pool,ids):return tls([pool[i]['endpoints'] for i in ids])
def cross(a,b):
 q=np.cross(a,b);return q[:2]/q[2]
top=line(data['top'],[4,15]);sideA=line(data['top'],[1]);backB=line(long,[1]);floorfront=line(data['floorA'],[1]);floorfrontB=line(data['floorB'],[0]);verticalA=line(data['floorA'],[2]);verticalB=line(data['floorB'],[1])
refined={7:cross(top,sideA),8:cross(top,backB),9:cross(floorfront,verticalA),10:cross(floorfrontB,verticalB)}
row=next(r for r in json.loads((R/'out_X/camera_fit_X.json').read_text()) if r['shot']==shot);c=json.loads((R/f'out_X/{shot}_camera.json').read_text());P=np.array(row['controls_world']);old=np.array(row['controls_observed_native_px']);uv=old.copy()
for i,v in refined.items():uv[i]=v
rv=Rotation.from_matrix(c['R']).as_rotvec();base=np.r_[rv,c['C'],np.log(c['f']),(np.array(c['principal_point_native_px'])-[c['W']/2,c['H']/2])/c['W'],0.]
results=[]
for mode,n in [('square_pixels',9),('effective_aspect',10)]:
 def project(x):
  z=np.zeros(10);z[:len(x)]=x;q=(P-z[3:6])@Rotation.from_rotvec(z[:3]).as_matrix().T;a=q[:,:2]/q[:,2:];a[:,1]*=np.exp(z[9]);return a*np.exp(z[6])+[c['W']/2,c['H']/2]+z[7:9]*c['W']
 lo=np.r_[rv-.15,np.array(c['C'])-1,np.log(c['f']*.7),-.05,-.05,-.03][:n];hi=np.r_[rv+.15,np.array(c['C'])+1,np.log(c['f']*1.3),.05,.05,.03][:n]
 fit=least_squares(lambda x:(project(x)-uv).ravel(),base[:n],bounds=(lo,hi),max_nfev=5000,xtol=1e-12,ftol=1e-12,gtol=1e-12);err=np.linalg.norm(project(fit.x)-uv,axis=1)
 results.append({'model':mode,'rms':float(np.sqrt((err**2).mean())),'max':float(err.max()),'parameters':fit.x.tolist(),'residuals':err.tolist(),'observations_original':old.tolist(),'observations_refined':uv.tolist(),'refined_ids':list(refined),'old_camera_rms_against_refined_observations':float(np.sqrt(np.mean(np.sum((project(base[:n])-uv)**2,axis=1)))),'status':'native original-photo edge intersection refinement; world coordinates unchanged; no rejected observations; diagnostic pending validation'})
# Diagnostic only. The selected camera is reproduced by
# calibrate_u2_native_conservative_Y.py; never overwrite it with this wide fit.
(O/'native_edge_camera_u2_wide_bounds.json').write_text(json.dumps(results,indent=2));print(json.dumps([{'model':r['model'],'rms':r['rms'],'max':r['max'],'observations_refined':r['observations_refined'][7:],'parameters':r['parameters'][9:]} for r in results],indent=2))
