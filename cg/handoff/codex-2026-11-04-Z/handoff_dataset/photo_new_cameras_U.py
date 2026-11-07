from pathlib import Path
import numpy as np,json,math,cv2
from PIL import Image
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parent;O=R/'out/photo_geometry_U';O.mkdir(exist_ok=True)
T=R/'out/photo_composite_T';h=2.486115036375903
nodes=np.array([[(x-24)/35.2,(473-y)/35.2] for x,y in [(24,473),(43,427),(76,336),(109,245),(142,154),(175,63),(194,14)]])
def caminit(eye,target,f,W=960,H=1280):
 fw=np.array(target)-eye;fw=fw/np.linalg.norm(fw);right=np.cross(fw,[0,0,1]);right/=np.linalg.norm(right);down=np.cross(fw,right);return dict(W=W,H=H,C=list(eye),R=np.array([right,down,fw]).tolist(),f=f,k1=0,k2=0)
def fit(n,c,pts,uv,lines=()):
 pts=np.array(pts,float);uv=np.array(uv,float);rv=Rotation.from_matrix(c['R']).as_rotvec();x0=np.r_[rv,c['C'],np.log(c['f'])]
 def project(x,p):
  q=(np.array(p)-x[3:6])@Rotation.from_rotvec(x[:3]).as_matrix().T;return q[:,:2]/q[:,2:]*np.exp(x[6])+[c['W']/2,c['H']/2]
 def res(x):
  rr=list(((project(x,pts)-uv)/3).ravel());rot=Rotation.from_rotvec(x[:3]).as_matrix()
  for vec,a,b in lines:
   q=rot@np.array(vec);vp=q[:2]/q[2]*np.exp(x[6])+[c['W']/2,c['H']/2];d=vp-a;d/=np.linalg.norm(d);v=np.array(b)-a;rr.append((d[0]*v[1]-d[1]*v[0])/3)
  rr.extend((x[:3]-rv)/.18);rr.append((x[5]-1.5)/.25);rr.append((x[6]-np.log(c['f']))/.4);return rr
 lo=np.full(7,-np.inf);hi=np.full(7,np.inf)
 if n=='n01':
  lo[3:5]=[7.2,2.0];hi[3:5]=[9.3,4.35];x0=np.maximum(np.minimum(x0,hi-1e-6),lo+1e-6)
 f=least_squares(res,x0,bounds=(lo,hi),max_nfev=3000,loss='soft_l1',f_scale=5);pred=project(f.x,pts);err=np.linalg.norm(pred-uv,axis=1);c.update(C=f.x[3:6].tolist(),R=Rotation.from_rotvec(f.x[:3]).as_matrix().tolist(),f=float(np.exp(f.x[6])),revision='U',window_height_m=h,status='architectural controls and visible counter where available; approximate raster plan; no EXIF focal length',fit_controls={'world':pts.tolist(),'pixels':uv.tolist(),'predicted':pred.tolist(),'residuals_px':err.tolist()});(O/f'{n}_camera.json').write_text(json.dumps(c,indent=2),encoding='utf8');print(n,'C',np.round(c['C'],2),'f',round(c['f']),'RMS',round(float(np.sqrt((err**2).mean())),2),'errors',np.round(err,1),flush=True)
 im=cv2.imread(str(R/f'images/photos/{n}.jpg'))
 for a,b in zip(uv,pred):cv2.circle(im,tuple(np.rint(a).astype(int)),4,(255,255,0),-1);cv2.circle(im,tuple(np.rint(b).astype(int)),6,(0,0,255),1);cv2.line(im,tuple(np.rint(a).astype(int)),tuple(np.rint(b).astype(int)),(0,0,255),2)
 cv2.imwrite(str(O/f'{n}_controls.jpg'),im);return c
# Retain corner identity in corner photograph, fit known balcony direction too.
p=[];uv=[]
for k,top,bot in [(0,[507,584],[507,713]),(1,[559,574],[559,725]),(2,[702,557],[702,754])]:p.extend([[*nodes[k],h],[*nodes[k],0]]);uv.extend([top,bot])
c=json.loads((T/'p09_camera.json').read_text());c.update(W=960,H=1280,f=c['f']*960/c['W']);fit('n01',c,p,uv,[([1,0,0],np.array([5,520]),np.array([438,574]))])
# Balcony jambs registered on the original floorplan.
xl=(103-24)/35.2;xr=(324-24)/35.2
p=[[xr,0,h],[xl,0,h],[xl,0,0],[xr,0,0]]
fit('n02',caminit(np.array([4.,7.,1.5]),[4,0,1.5],600),p,[[58,554],[539,551],[539,745],[58,755]], [([* (nodes[6]-nodes[0]),0],np.array([765,442]),np.array([937,236]))])
p2=p+[[9.4,4.4,2.346],[9.4,.3,2.346],[9.4,.3,0],[9.4,4.4,0]]
fit('n03',caminit(np.array([3.,5.,1.5]),[8,0,1.35],600),p2,[[400,578],[910,520],[910,801],[400,742],[25,544],[355,578],[355,732],[25,798]])
p=[];uv=[]
for k,top,bot in [(0,[213,560],[214,725]),(1,[274,562],[274,725]),(2,[455,565],[455,722]),(3,[620,567],[620,720])]:p.extend([[*nodes[k],h],[*nodes[k],0]]);uv.extend([top,bot])
p.append([*nodes[4],h]);uv.append([778,570])
for px,py,z,u,v in [(159,230,.91,702,666),(194,242,.91,753,677),(159,230,0,702,727),(194,242,0,753,750)]:p.append([(px-24)/35.2,(473-py)/35.2,z]);uv.append([u,v])
c=caminit(np.array([8.4,.9,1.5]),[1.5,5,1.5],650);fit('n04',c,p,uv)
# Correct p01 pane identity in continuity with counter-anchored u2.
c=json.loads((T/'p01_camera.json').read_text());p=[];uv=[]
for k,top,bot in [(2,[620,674],[620,1276]),(3,[1280,676],[1280,1277])]:p.extend([[*nodes[k],h],[*nodes[k],0]]);uv.extend([top,bot])
sf=c['W']/1368;c['C']=(np.array(c['C'])-np.r_[nodes[3]-nodes[2],0]).tolist();fit('p01',c,p,np.array(uv)*sf)
