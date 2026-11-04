import json,numpy as np,sys
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation as Rot
sys.path.insert(0,'/work/new')
c=json.load(open('/work/hj/handoff_dataset/out/photo_geometry_U/n04_camera.json'));s0=1086/960
cur=json.load(open('/work/new/n04_camera_Z3.json'))
W,H=1086,1448
ctrl_w=np.array(c['fit_controls']['world'])[2:];ctrl_p=np.array(c['fit_controls']['pixels'])[2:]*s0
line_p=np.array([[177,907],[127,1060],[80,1213],[27,1367]],float)
# stripe pixels: from the current camera's plan detection (slope .26; feet 4.21,5.59,7.93 -> true 4.15,5.43,7.44)
Rc,Cc,fc=np.array(cur['R']),np.array(cur['C']),cur['f'];ppc=np.array(cur['principal_point_native_px'])
def P(R,C,f,pp,X):q=(X-C)@R.T;return q[:,:2]/q[:,2:]*f+pp
stripes=[]
for fd,ft in [(4.21,4.15),(5.59,5.43),(7.93,7.44)]:
    ys=np.arange(1.5,4.1,0.25);Xw=np.c_[fd+0.26*ys,ys,np.zeros_like(ys)];px=P(Rc,Cc,fc,ppc,Xw)
    for p in px:
        if 0<p[0]<W and 0<p[1]<H:stripes.append((p,ft))
print('stripe pts',len(stripes))
def unpack(x):return Rot.from_rotvec(x[:3]).as_matrix(),x[3:6],x[6],x[7:9],x[9]
def bpf(R,C,f,pp,px):
    d=(R.T@np.c_[(px-pp)/f,np.ones(len(px))].T).T;t=-C[2]/d[:,2];return C+t[:,None]*d
def res(x):
    R,C,f,pp,s=unpack(x);r1=(P(R,C,f,pp,ctrl_w)-ctrl_p).ravel()
    g=bpf(R,C,f,pp,line_p);r2=np.c_[(P(R,C,f,pp,np.c_[g[:,0],np.zeros(len(g)),np.zeros(len(g))])-line_p)].ravel()
    sp=np.array([a for a,_ in stripes]);ft=np.array([b for _,b in stripes]);g=bpf(R,C,f,pp,sp)
    tgt=np.c_[ft+s*g[:,1],g[:,1],np.zeros(len(g))];r3=(P(R,C,f,pp,tgt)-sp).ravel()*0.7
    return np.r_[r1,r2,r3]
x0=np.r_[Rot.from_matrix(Rc).as_rotvec(),Cc,fc,ppc,0.19]
lo=np.r_[-7,-7,-7,7.0,0.25,1.2,350,W/2-80,H/2-150,0.10];hi=np.r_[7,7,7,9.38,3.5,1.8,900,W/2+80,H/2+150,0.45]
sol=least_squares(res,np.clip(x0,lo+1e-6,hi-1e-6),bounds=(lo,hi),loss='soft_l1',f_scale=5)
R,C,f,pp,s=unpack(sol.x);r=res(sol.x).reshape(-1,2);n1=len(ctrl_w);n2=len(line_p)
e=np.sqrt((r**2).sum(1));print('ctrl',e[:n1].round(1),'line',e[n1:n1+n2].round(1),'stripes rms',np.sqrt((e[n1+n2:]**2).mean()).round(2),'C',C.round(3),'f',round(f,1),'pp',pp.round(1),'sun slope',round(s,3))
json.dump({'W':W,'H':H,'C':C.tolist(),'R':R.tolist(),'f':float(f),'principal_point_native_px':pp.tolist(),'revision':'Z3b','sun_slope_dXdY':float(s),'status':'refit with U architectural controls (corner excluded), balcony floor line, and photographed mullion-shadow lines tied to the n03 mullion feet (shadow lines are straight floor lines through the fixed frames); free principal point for listing-photo vertical correction; approximate plan','residuals_px':{'controls':e[:n1].tolist(),'balcony_line':e[n1:n1+n2].tolist(),'stripes_rms':float(np.sqrt((e[n1+n2:]**2).mean()))}},open('/work/new/n04_camera_Z3b.json','w'),indent=2)
