import json,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation as Rot
c=json.load(open('/work/hj/handoff_dataset/out/photo_geometry_U/n04_camera.json'));s=1086/960
W,H=1086,1448;cx,cy=W/2,H/2
ctrl_w=np.array(c['fit_controls']['world']);ctrl_p=np.array(c['fit_controls']['pixels'])*s
line_p=np.array([[177,907],[127,1060],[80,1213],[27,1367]],float)  # balcony glazing floor line (Y=0,z=0)
R0=np.array(c['R']);C0=np.array(c['C']);f0=c['f']*s
def unpack(x):return Rot.from_rotvec(x[:3]).as_matrix(),x[3:6],x[6]
def proj(R,C,f,P):q=(P-C)@R.T;return q[:,:2]/q[:,2:]*f+[cx,cy]
def res(x,wline=1.0):
    R,C,f=unpack(x);r1=(proj(R,C,f,ctrl_w)-ctrl_p).ravel()
    d=(R.T@np.c_[(line_p-[cx,cy])/f,np.ones(len(line_p))].T).T;t=-C[2]/d[:,2];Y=C[1]+t*d[:,1]
    # convert floor Y error to pixels approximately via local scale: project points shifted
    pts=np.c_[C[0]+t*d[:,0],np.zeros(len(t)),np.zeros(len(t))]
    r2=(proj(R,C,f,pts)-line_p).ravel()*wline
    return np.r_[r1,r2]
x0=np.r_[Rot.from_matrix(R0).as_rotvec(),C0,f0]
for name,wl in [('U_controls_only',0.0),('with_balcony_line',1.0)]:
    sol=least_squares(lambda x:res(x,wl),x0,loss='soft_l1',f_scale=6)
    R,C,f=unpack(sol.x);r=res(sol.x,1.0).reshape(-1,2);rc=r[:len(ctrl_w)];rl=r[len(ctrl_w):]
    print(name,'ctrl rms',np.sqrt((rc**2).sum(1).mean()).round(2),'max',np.sqrt((rc**2).sum(1)).max().round(2),'line rms',np.sqrt((rl**2).sum(1).mean()).round(2),'C',C.round(3),'f',round(f,1),'fwd',R[2].round(3))
    if wl:json.dump({'W':W,'H':H,'C':C.tolist(),'R':R.tolist(),'f':float(f),'principal_point_native_px':[cx,cy],'revision':'Z3','status':'refit at 1086x1448: U architectural controls plus balcony glazing floor line; approximate raster plan','residuals_px':{'controls_rms':float(np.sqrt((rc**2).sum(1).mean())),'controls_max':float(np.sqrt((rc**2).sum(1)).max()),'balcony_line_rms':float(np.sqrt((rl**2).sum(1).mean()))}},open('/work/new/n04_camera_Z3.json','w'),indent=2)
print('--- bounded')
lo=np.r_[-np.pi*np.ones(3)*2,7.0,0.3,1.2,350];hi=np.r_[np.pi*np.ones(3)*2,9.3,3.5,1.8,900]
best=None
for f0s in [450,550,650,750]:
  for cyy in [0.6,1.0,1.5,2.0]:
    x0b=np.r_[Rot.from_matrix(R0).as_rotvec(),8.8,cyy,1.45,f0s];x0b=np.clip(x0b,lo+1e-6,hi-1e-6)
    sol=least_squares(lambda x:res(x,1.0),x0b,bounds=(lo,hi),loss='soft_l1',f_scale=6)
    if best is None or sol.cost<best.cost:best=sol
R,C,f=unpack(best.x);r=res(best.x,1.0).reshape(-1,2);rc=r[:len(ctrl_w)];rl=r[len(ctrl_w):]
print('bounded ctrl rms',np.sqrt((rc**2).sum(1).mean()).round(2),'per-ctrl',np.sqrt((rc**2).sum(1)).round(1),'line',np.sqrt((rl**2).sum(1)).round(1),'C',C.round(3),'f',round(f,1))
print('--- drop corner')
keep=np.ones(len(ctrl_w),bool);keep[:2]=False
ctrl_w,ctrl_p=ctrl_w[keep],ctrl_p[keep]
lo=np.r_[-np.pi*np.ones(3)*2,7.0,0.25,1.2,350];hi=np.r_[np.pi*np.ones(3)*2,9.38,3.5,1.8,900]
best=None
for f0s in [450,550,650,750]:
  for cyy in [0.5,1.0,1.5]:
    x0b=np.clip(np.r_[Rot.from_matrix(R0).as_rotvec(),8.8,cyy,1.45,f0s],lo+1e-6,hi-1e-6)
    sol=least_squares(lambda x:res(x,1.0),x0b,bounds=(lo,hi),loss='soft_l1',f_scale=6)
    if best is None or sol.cost<best.cost:best=sol
R,C,f=unpack(best.x);r=res(best.x,1.0).reshape(-1,2);rc=r[:len(ctrl_w)];rl=r[len(ctrl_w):]
allr=np.r_[np.sqrt((rc**2).sum(1)),np.sqrt((rl**2).sum(1))]
print('ctrl',np.sqrt((rc**2).sum(1)).round(1),'line',np.sqrt((rl**2).sum(1)).round(1),'rms_all',np.sqrt((allr**2).mean()).round(2),'C',C.round(3),'f',round(f,1),'fwd',R[2].round(3))
json.dump({'W':W,'H':H,'C':C.tolist(),'R':R.tolist(),'f':float(f),'principal_point_native_px':[cx,cy],'revision':'Z3','status':'refit at 1086x1448 from U controls (two room-corner points excluded: 33 px outliers, corner misidentified) plus 4 balcony glazing floor-line points; camera bounded inside the room; approximate raster plan, not surveyed','residuals_px':{'controls':np.sqrt((rc**2).sum(1)).tolist(),'balcony_line':np.sqrt((rl**2).sum(1)).tolist(),'rms_all':float(np.sqrt((allr**2).mean()))}},open('/work/new/n04_camera_Z3.json','w'),indent=2)
