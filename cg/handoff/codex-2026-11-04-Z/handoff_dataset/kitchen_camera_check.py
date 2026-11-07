from pathlib import Path
import numpy as np,json
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_S'
c=json.loads((R/'calib/p13_cam.json').read_text());rot=np.array(c['R'])@np.diag([-1,-1,1]);f=c['f'];W,H=3024,4032
uv=np.array([[350,1075],[630,1145],[960,1040],[862,994]],float)*W/1368
rays=np.array([rot.T@np.r_[(p-[W/2,H/2])/f,1] for p in uv]);q=rays/rays[:,2:]
width=np.linalg.norm(np.array([(194-159)/35.2,(230-242)/35.2]));dz=width/np.linalg.norm(q[1,:2]-q[0,:2])
A=np.array([(159-24)/35.2,(473-230)/35.2,.91]);C=A+dz*q[0];C[2]=.91+dz
pts=C-dz*q
report={'C':C.tolist(),'R':rot.tolist(),'f':f,'reconstructed_island_top':pts.tolist(),'note':'diagnostic reconstruction constrained only by assumed near-edge width and inherited camera VP; NOT approved architecture'}
(O/'p13_island_diagnosis.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
