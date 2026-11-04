from pathlib import Path
import json,math,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path('handoff_dataset');O=R/'out/photo_geometry_U';c=json.loads((R/'out/photo_composite_T/u2_camera.json').read_text());sf=c['W']/1368;nodes=np.array([[(x-24)/35.2,(473-y)/35.2] for x,y in [(24,473),(43,427),(76,336),(109,245),(142,154),(175,63),(194,14)]]);h=c['window_height_m'];rv=Rotation.from_matrix(c['R']).as_rotvec();results=[]
for offset in [1,2]:
 p=[];uv=[]
 for k,(bot,top) in enumerate(zip([[139,663],[563,655],[937,648]],[[132,279],[562,291],[945,306]])):
  p.extend([[*nodes[k+offset],0],[*nodes[k+offset],h]]);uv.extend([bot,top])
 p.extend([[*nodes[offset+3],h]]);uv.extend([[1277,316]])
 # Counter near end, including its actual height on the plate.
 for px,py,z,u,v in [(159,230,.91,1135,535),(194,242,.91,1256,552),(159,230,0,1133,685),(194,242,0,1254,730)]:p.append([(px-24)/35.2,(473-py)/35.2,z]);uv.append([u,v])
 p=np.array(p);uv=np.array(uv)
 def project(x):
  q=(p-x[3:6])@Rotation.from_rotvec(x[:3]).as_matrix().T;return(q[:,:2]/q[:,2:]*np.exp(x[6])+[c['W']/2,c['H']/2])/sf
 def res(x):return np.r_[(project(x)-uv).ravel()/3,(x[:3]-rv)/.07,(x[5]-1.44)/.2,(x[6]-math.log(c['f']))/.2]
 x0=np.r_[rv,c['C'],math.log(c['f'])];x0[3:5]-=(nodes[2]-nodes[offset]);f=least_squares(res,x0,max_nfev=2000);err=np.linalg.norm(project(f.x)-uv,axis=1)
 print('firstD',offset,'C',np.round(f.x[3:6],3),'errors',np.round(err,1),'RMS',np.sqrt((err**2).mean()))
 row=dict(first_visible_mullion=offset,rms_ref_px=float(np.sqrt((err**2).mean())),residuals_ref_px=err.tolist());results.append(row)
 if offset==1:
  c.update(C=f.x[3:6].tolist(),R=Rotation.from_rotvec(f.x[:3]).as_matrix().tolist(),f=float(np.exp(f.x[6])),revision='U',status='window plus actual island near-face controls; T pane shift rejected by counter reprojection',fit_controls={'world':p.tolist(),'pixels_ref1368':uv.tolist(),'predicted_ref1368':project(f.x).tolist()});(O/'u2_camera.json').write_text(json.dumps(c,indent=2),encoding='utf8')
(O/'u2_pane_hypothesis_test.json').write_text(json.dumps(results,indent=2),encoding='utf8')
