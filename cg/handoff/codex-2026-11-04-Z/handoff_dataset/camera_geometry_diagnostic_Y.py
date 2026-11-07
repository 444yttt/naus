from pathlib import Path
import numpy as np,json,math
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parent;O=R/'out_Y'
row=next(x for x in json.loads((R/'out_X/camera_fit_X.json').read_text()) if x['shot']=='u2')
c=json.loads((R/'out_X/u2_camera.json').read_text());P=np.array(row['controls_world']);uv=np.array(row['controls_observed_native_px']);rv=Rotation.from_matrix(c['R']).as_rotvec();base=np.r_[rv,c['C'],np.log(c['f']),((np.array(c['principal_point_native_px'])-[c['W']/2,c['H']/2])/c['W'])]
t=np.array([.9375,2.58522727]);t/=np.linalg.norm(t);n=np.array([t[1],-t[0]])
reports=[]
for bound in [.02,.04,.08]:
 x0=np.r_[base,np.zeros(7)]
 lo=np.r_[rv-.15,np.array(c['C'])-1,np.log(c['f']*.7),-.05,-.05,[-bound]*4,-.05,-bound,-np.deg2rad(.5)]
 hi=np.r_[rv+.15,np.array(c['C'])+1,np.log(c['f']*1.3),.05,.05,[bound]*4,.05,bound,np.deg2rad(.5)]
 def geometry(x):
  p=P.copy();theta=x[15];rot=np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
  for i in range(7):
   j=i//2;p[i,:2]=rot@P[i,:2]+t*x[9+j]+n*x[14]
   if p[i,2]>1:p[i,2]+=x[13]
  return p
 def project(x):
  q=(geometry(x)-x[3:6])@Rotation.from_rotvec(x[:3]).as_matrix().T
  return q[:,:2]/q[:,2:]*np.exp(x[6])+[c['W']/2,c['H']/2]+x[7:9]*c['W']
 fit=least_squares(lambda x:np.r_[(project(x)-uv).ravel(),x[9:13]/bound*1.5,x[13]/.05*1.5,x[14]/bound*1.5,x[15]/np.deg2rad(.5)*1.5],x0,bounds=(lo,hi),max_nfev=4000,xtol=1e-12,ftol=1e-12,gtol=1e-12)
 err=np.linalg.norm(project(fit.x)-uv,axis=1)
 reports.append({'bound_m':bound,'rms_px':float(np.sqrt(np.mean(err**2))),'max_px':float(err.max()),'post_longitudinal_adjustments_m':fit.x[9:13].tolist(),'top_height_adjustment_m':float(fit.x[13]),'plane_offset_m':float(fit.x[14]),'plane_angle_deg':float(np.rad2deg(fit.x[15])),'world_original':P.tolist(),'world_refined':geometry(fit.x).tolist(),'observations_unchanged':uv.tolist(),'predicted':project(fit.x).tolist(),'fit_vector':fit.x.tolist(),'status':'DIAGNOSTIC ONLY: unmeasured architecture refinement, not applied to delivery; requires independent image-edge validation'})
(O/'camera_geometry_diagnostic.json').write_text(json.dumps(reports,indent=2));print(json.dumps([{k:v for k,v in r.items() if k not in ['world_original','world_refined','observations_unchanged','predicted','fit_vector']} for r in reports],indent=2))
