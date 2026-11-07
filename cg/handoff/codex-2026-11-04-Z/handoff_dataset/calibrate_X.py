from pathlib import Path
import json,math,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;W=R/'out/photo_final_W';O=R/'out_X';(O/'previews').mkdir(exist_ok=True)
validation=json.loads((W/'delivery/details/camera_fit_unchanged_from_V.json').read_text());rows=[]
for shot in ['u1','u2','p09','p01','p13']:
 c=json.loads((W/f'{shot}_camera.json').read_text());row=next(v for v in validation if v['shot']==shot)
 if shot in ['u2','p13']:
  p=np.array(row['controls_world']);uv=np.array(row['controls_observed_native_px']);rv=Rotation.from_matrix(c['R']).as_rotvec();x0=np.r_[rv,c['C'],math.log(c['f']),0.,0.]
  def project(x):
   q=(p-x[3:6])@Rotation.from_rotvec(x[:3]).as_matrix().T
   return q[:,:2]/q[:,2:]*np.exp(x[6])+np.array([c['W']/2,c['H']/2])+x[7:9]*c['W']
  # Optimise the exact W observations: no relabelling, deleted controls, new
  # geometry, per-point corrections or nonlinear photographic warp.
  lo=np.r_[rv-.12,np.array(c['C'])-1.0,math.log(c['f']*.7),-.025,-.025];hi=np.r_[rv+.12,np.array(c['C'])+1.0,math.log(c['f']*1.3),.025,.025]
  fit=least_squares(lambda x:(project(x)-uv).ravel(),x0,bounds=(lo,hi),max_nfev=3000,xtol=1e-12,ftol=1e-12,gtol=1e-12)
  pred=project(fit.x);err=np.linalg.norm(pred-uv,axis=1);rms=float(np.sqrt(np.mean(err**2)))
  c.update(R=Rotation.from_rotvec(fit.x[:3]).as_matrix().tolist(),C=fit.x[3:6].tolist(),f=float(np.exp(fit.x[6])),principal_point_native_px=(np.array([c['W']/2,c['H']/2])+fit.x[7:9]*c['W']).tolist(),revision='X',status='bounded pinhole camera refit, original W architectural controls retained; approximate raster room geometry')
  for key in ['architecture_controls','fit_controls','anchors','anchor_rms_px']:
   if key in c:c['baseline_W_'+key]=c.pop(key)
  row={**row,'W_rms_native_px':row['architecture_fit_rms_native_px'],'architecture_fit_rms_native_px':rms,'architecture_fit_max_native_px':float(err.max()),'controls_projected_native_px':pred.tolist(),'residuals_native_px':err.tolist(),'target_7px_pass':rms<=7,'camera_changed':True,'principal_shift_fraction_width':fit.x[7:9].tolist(),'reason_if_target_missed':'Fixed approximate raster-plan geometry and unchanged control observations are not mutually consistent with a single bounded pinhole camera.' if rms>7 else None}
  row['architecture_fit_rms_at_1368_width_px']=rms*1368/c['W'];row['camera_estimate']={k:c[k] for k in ['C','R','f','principal_point_native_px']}
  for key in list(row):
   if key.startswith('floor_'):row.pop(key)
  im=Image.open(R/f'images/photos_srgb/{shot}.png').convert('RGB');im.thumbnail((1368,1824));d=ImageDraw.Draw(im);sf=im.width/c['W']
  for j,(a,b) in enumerate(zip(uv*sf,pred*sf)):
   d.line([tuple(a),tuple(b)],fill='red',width=3);d.ellipse((a[0]-4,a[1]-4,a[0]+4,a[1]+4),fill='cyan');d.ellipse((b[0]-6,b[1]-6,b[0]+6,b[1]+6),outline='red',width=2);d.text(tuple(a+[7,-10]),str(j),fill='cyan',stroke_width=1,stroke_fill='black')
  im.save(O/f'previews/{shot}_camera_fit_X.jpg',quality=95)
  print(shot,'RMS',row['W_rms_native_px'],'->',rms,'max',err.max(),'principal',fit.x[7:9],flush=True)
 else:row={**row,'W_rms_native_px':row['architecture_fit_rms_native_px'],'camera_changed':False,'camera_numeric_difference':0}
 (O/f'{shot}_camera.json').write_text(json.dumps(c,indent=2));rows.append(row)
(O/'camera_fit_X.json').write_text(json.dumps(rows,indent=2))
