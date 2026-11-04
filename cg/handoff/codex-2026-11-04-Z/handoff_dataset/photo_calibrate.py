"""Photographic camera fitting, retaining a common metric plan frame."""
from pathlib import Path
import json, math
import numpy as np
import cv2
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from PIL import Image, ExifTags
R=Path(__file__).resolve().parent
O=R/'out/photo_composite_S';O.mkdir(exist_ok=True)
metadata={}
for p in (R/'images/photos').glob('*.jpg'):
 im=Image.open(p)
 ex=im.getexif();ev={ExifTags.TAGS.get(k,str(k)):str(v) for k,v in ex.items()}
 try:ev.update({ExifTags.TAGS.get(k,str(k)):str(v) for k,v in ex.get_ifd(34665).items()})
 except Exception:pass
 metadata[p.stem]={'size':list(im.size),'exif':ev}
(O/'photo_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')

def initial(name):
 c=json.loads((R/f'calib/{name}_calib.json').read_text())
 W,H=metadata[name]['size'];rot=np.array(c['R'])
 if name in ['u1','u2','p01','p03']:
  rot=rot@np.diag([-1,-1,1]);xy={'u1':[1.30,2.115],'u2':[7.25,.99],'p01':[7.0,2.0],'p03':[4.,3.]}[name]
 elif name=='p09':xy=[8.68,4.06]
 else:xy=[7.25,.99]
 return dict(W=W,H=H,f=c['f'],R=rot.tolist(),C=[*xy,c['h']],k1=0.,k2=0.)

def project(c,P):
 P=np.array(P,float);v=(P-np.array(c['C']))@np.array(c['R']).T
 q=v[:,:2]/v[:,2:];rr=(q*q).sum(1)
 q*=1+c.get('k1',0)*rr[:,None]+c.get('k2',0)*rr[:,None]**2
 return q*c['f']+[c['W']/2,c['H']/2]

c=initial('u1');W,H=c['W'],c['H'];factor=W/1368
# Manually identified inside grey-wall corners in original photo, scaled from 1368-wide view.
# Top of grey wall is below the ceiling beam: its height is fitted, not treated as room ceiling.
uv=np.array([[314,1029],[822,1016],[822,731],[305,731]],float)*factor
rot0=Rotation.from_matrix(c['R']).as_rotvec();C0=np.array(c['C']);f0=c['f']
x0=np.r_[rot0,C0,math.log(f0),2.45]
def unpack(x):
 d={**c,'R':Rotation.from_rotvec(x[:3]).as_matrix().tolist(),'C':x[3:6].tolist(),'f':math.exp(x[6])}
 return d
def worldpts(z):return [[9.4,4.4,0],[9.4,.3,0],[9.4,.3,z],[9.4,4.4,z]]
def residual(x):
 d=unpack(x)
 data=(project(d,worldpts(x[7]))-uv).ravel()/3
 # A planar wall alone has scale/pose ambiguities: retain camera/metric priors explicitly.
 prior=np.r_[(x[:3]-rot0)/.025,(x[3:5]-C0[:2])/.25,(x[5]-C0[2])/.12,(x[6]-math.log(f0))/.07,(x[7]-2.45)/.20]
 return np.r_[data,prior]
fit=least_squares(residual,x0,max_nfev=1000)
c=unpack(fit.x);pred=project(c,worldpts(fit.x[7]));err=np.linalg.norm(pred-uv,axis=1)
c.update(shot='u1',status='manually identified grey-wall corners + inherited floor-VP orientation priors; independent floor checks required',wall_top_z=float(fit.x[7]),observations={'world':worldpts(fit.x[7]),'pixels':uv.tolist(),'predicted':pred.tolist(),'corner_rms_px':float(np.sqrt(np.mean(err**2)))},distortion_status='k1=k2=0 initial; residual straight-line distortion not yet measured')
(O/'u1_camera.json').write_text(json.dumps(c,indent=2),encoding='utf8')
im=cv2.imread(str(R/'images/photos/u1.jpg'))
for p,q in zip(uv,pred):
 cv2.circle(im,tuple(np.rint(p).astype(int)),16,(0,255,255),4)
 cv2.circle(im,tuple(np.rint(q).astype(int)),8,(0,255,0),-1)
for a,b in zip(pred,np.roll(pred,-1,axis=0)):cv2.line(im,tuple(a.astype(int)),tuple(b.astype(int)),(0,255,0),5)
# Approved rug outline and sofa feet in the common plan frame.
layout=json.loads((R/'out/layout_Q.json').read_text(encoding='utf-8-sig'))
pts=[[5.2,.35,0],[8.7,.35,0],[8.7,4.35,0],[5.2,4.35,0]]
pr=project(c,pts)
for a,b in zip(pr,np.roll(pr,-1,axis=0)):cv2.line(im,tuple(a.astype(int)),tuple(b.astype(int)),(0,180,255),5)
cv2.putText(im,f"u1 wall-corner fit RMS {c['observations']['corner_rms_px']:.1f}px; distortion pending",(70,110),cv2.FONT_HERSHEY_SIMPLEX,2,(0,255,255),4)
cv2.imwrite(str(O/'u1_camera_check.jpg'),im,[cv2.IMWRITE_JPEG_QUALITY,94])
print(json.dumps({k:c[k] for k in ['C','f','wall_top_z','observations']},indent=2))

# Other photographs use the same global plan. Cross-view mullion anchors are
# inferred from u2 and explicitly recorded as such, not called survey control.
d=np.array([math.cos(math.radians(70.7)),math.sin(math.radians(70.7))])
def floorpoint(cam,uv):
 ray=np.array(cam['R']).T@np.r_[(np.array(uv)-[cam['W']/2,cam['H']/2])/cam['f'],1.]
 return np.array(cam['C'])-cam['C'][2]/ray[2]*ray
u2=initial('u2');anchors=[]
for px in [[185,884],[750,873],[1249,864]]:
 p=floorpoint(u2,np.array(px)*u2['W']/1824);xy=d*np.dot(p[:2],d);anchors.append([*xy,0])
u2.update(shot='u2',status='inherited camera; diagonal floor-line adjustment below',distortion_status='no extra warp; source appears electronically corrected; per-shot curvature validation pending')
# Correct normal distance so the real diagonal floor line projects onto the plate.
obs=np.array([[185,884],[750,873],[1249,864]])*u2['W']/1824
norm=np.array([-d[1],d[0]])
def u2res(x):
 cc={**u2,'C':(np.array(u2['C'])+np.r_[norm*x[0],x[1]]).tolist()}
 return np.r_[(project(cc,anchors)-obs).ravel()/3,x/[.15,.08]]
fit2=least_squares(u2res,[0.,0.]);u2['C']=(np.array(u2['C'])+np.r_[norm*fit2.x[0],fit2.x[1]]).tolist()
u2['anchors']={'world':anchors,'pixels':obs.tolist(),'source':'mullion feet backprojected using inherited u2 calibration, then constrained to diagonal floor line'}
u2['anchor_rms_px']=float(np.sqrt(np.mean((project(u2,anchors)-obs)**2)))
(O/'u2_camera.json').write_text(json.dumps(u2,indent=2),encoding='utf8')

for name,anchor,pix in [('p09',[0,0,0],[847,1046]),('p01',anchors[1],[620,1276]),('p03',anchors[0],[1090,1438])]:
 cc=initial(name);uv0=np.array(pix)*cc['W']/1368
 # Solve translation from one shared metric floor anchor and inherited orientation/height.
 ray=np.array(cc['R']).T@np.r_[(uv0-[cc['W']/2,cc['H']/2])/cc['f'],1.]
 cc['C']=(np.array(anchor)+cc['C'][2]/ray[2]*ray).tolist();cc['C'][2]=initial(name)['C'][2]
 cc.update(shot=name,status='inherited VP orientation + cross-view floor anchor; first iteration, independent validation pending',anchor={'world':anchor,'pixel':uv0.tolist(),'source':'architectural floor intersection' if name=='p09' else 'same diagonal-window mullion as u2'},distortion_status='no additional warp in first iteration; per-shot residual curvature validation pending')
 (O/f'{name}_camera.json').write_text(json.dumps(cc,indent=2),encoding='utf8')
 print(name,'camera',cc['C'])

# Kitchen view p13: metric island corners, with inherited VP orientation as prior.
pc=json.loads((R/'calib/p13_cam.json').read_text());p13={'W':metadata['p13']['size'][0],'H':metadata['p13']['size'][1],'f':pc['f'],'R':(np.array(pc['R'])@np.diag([-1,-1,1])).tolist(),'C':[5.8,4.8,1.5],'k1':0,'k2':0}
world=np.array([[(159-24)/35.2,(473-230)/35.2,.91],[(194-24)/35.2,(473-242)/35.2,.91],[(216-24)/35.2,(473-120)/35.2,.91],[(201-24)/35.2,(473-114)/35.2,.91]])
pixels=np.array([[350,1075],[630,1145],[960,1040],[862,994]],float)*p13['W']/1368
rv=Rotation.from_matrix(p13['R']).as_rotvec();xx=np.r_[rv,p13['C'],math.log(p13['f'])]
def unpack13(x):return {**p13,'R':Rotation.from_rotvec(x[:3]).as_matrix().tolist(),'C':x[3:6].tolist(),'f':math.exp(x[6])}
def res13(x):
 return np.r_[(project(unpack13(x),world)-pixels).ravel()/3,(x[:3]-rv)/.03,(x[5]-1.5)/.20,(x[6]-math.log(p13['f']))/.08]
ff=least_squares(res13,xx,max_nfev=1000);p13=unpack13(ff.x)
p13.update(shot='p13',status='approximate island footprint corners + inherited VP prior; not surveyed',anchor={'world':world.tolist(),'pixel':pixels.tolist()},corner_rms_px=float(np.sqrt(np.mean((project(p13,world)-pixels)**2))),distortion_status='no extra warp; independent curvature validation pending')
# The original plan tracing puts the kitchen's short return ~1.9m too far north.
# Reconstruct the existing countertop in the photo's inherited VP frame, using
# its near-edge width only as the metric prior. This is NOT independent validation.
rot=np.array(pc['R'])@np.diag([-1,-1,1]);f=pc['f']
rays=np.array([rot.T@np.r_[(p-[p13['W']/2,p13['H']/2])/f,1] for p in pixels]);q=rays/rays[:,2:]
nearwidth=np.linalg.norm(world[1,:2]-world[0,:2]);dz=nearwidth/np.linalg.norm(q[1,:2]-q[0,:2])
cam=world[0]+dz*q[0];cam[2]=.91+dz;island=cam-dz*q
p13.update(C=cam.tolist(),R=rot.tolist(),f=f,status='photo-inferred kitchen geometry: camera VP inherited; scale constrained by assumed1.052m near edge; not independently surveyed',island_top= island.tolist())
p13.pop('corner_rms_px',None)
(O/'p13_camera.json').write_text(json.dumps(p13,indent=2),encoding='utf8');print('p13',p13['C'],'photo-inferred island')
