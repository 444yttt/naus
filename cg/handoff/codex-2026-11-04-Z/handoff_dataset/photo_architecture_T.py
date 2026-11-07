"""Architecture-first shared camera fit, revision T.
Window IDs counted from acute corner, including the first short pane.
Plan is raster tracing, metric scale approximate. Camera priors not independent truth.
"""
from pathlib import Path
import json,math,cv2,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;O=R/'out/photo_geometry_T';O.mkdir(exist_ok=True)
# Pixel nodes on original 800x546 plan, centerline of glazing.
plan_nodes=[(24,473),(43,427),(76,336),(109,245),(142,154),(175,63),(194,14)]
xy=np.array([[(x-24)/35.2,(473-y)/35.2] for x,y in plan_nodes])
# All observation coordinates refer to a 1368px-wide unwarped photograph.
obs={
 'p03':[(0,0,[174,1190]),(1,0,[380,1244]),(2,0,[1090,1400]),(0,1,[174,615]),(1,1,[380,570]),(2,1,[1090,418])],
 'p09':[(0,0,[865,1050]),(1,0,[950,1066]),(2,0,[1240,1115]),(0,1,[865,840]),(1,1,[950,833]),(2,1,[1240,800])],
 'u2':[(2,0,[139,663]),(3,0,[563,655]),(4,0,[937,648]),(2,1,[132,279]),(3,1,[562,291]),(4,1,[945,306]),(5,1,[1277,316])],
 'p01':[(3,0,[620,1276]),(4,0,[1280,1277]),(3,1,[620,674]),(4,1,[1280,676])],
 # Kitchen floor controls are separate line constraints where countertop occludes feet.
 'p13':[(4,1,[568,727]),(5,1,[807,795]),(6,1,[879,811])]
}
# u2 observations converted from original1824 to1368 above; only 3 feet unobscured.
# p13 window back edge (not island) adds genuine non-collinear architectural control.
extra={}
names=list(obs);cameras={n:json.loads((R/f'out/photo_composite_S/{n}_camera.json').read_text()) for n in names}
rv0={n:Rotation.from_matrix(cameras[n]['R']).as_rotvec() for n in names}
x0=[2.4]
for n in names:
 c=cameras[n];x0.extend([*rv0[n],*c['C'],math.log(c['f'])])
x0=np.array(x0)
def unpack(x,n):
 i=1+names.index(n)*7;c={**cameras[n]};c.update(R=Rotation.from_rotvec(x[i:i+3]).as_matrix().tolist(),C=x[i+3:i+6].tolist(),f=float(np.exp(x[i+6])))
 return c

def project(c,p):
 q=(np.array(p)-c['C'])@np.array(c['R']).T
 return q[:,:2]/q[:,2:]*c['f']+[c['W']/2,c['H']/2]
def data(x,n):
 h=x[0];p=[[ *xy[k],h*z] for k,z,uv in obs[n]];uv=[uv for k,z,uv in obs[n]]
 for v,u in extra.get(n,[]):p.append([*v[:2],h if v[2]>0 else 0]);uv.append(u)
 return np.array(p),np.array(uv)
def residual(x):
 res=[(x[0]-2.4)/.2]
 for n in names:
  i=1+names.index(n)*7;c=unpack(x,n);p,uv=data(x,n);res.extend(((project(c,p)*1368/c['W']-uv)/3).ravel())
  # Retain VP estimates softly; allow positions to move when pane ID changes.
  res.extend((x[i:i+3]-rv0[n])/.035)
  if n=='p13':
   q=project(c,[[*xy[k],0] for k in [3,4,5]])*1368/c['W']
   # Exposed diagonal sill at image left. No hidden island corner treated as a window control.
   res.extend((q[:,1] + (114/350)*q[:,0] - 1337)/3)
   ip=[[(a-24)/35.2,(473-b)/35.2,.91] for a,b in [(159,230),(194,242),(216,182),(216,120),(201,114)]]
   iu=np.array([[350,1075],[630,1140],[960,1040],[949,991],[862,994]])
   res.extend(((project(c,ip)*1368/c['W']-iu)/8).ravel())
   fp=[[*ip[k][:2],0] for k in [0,1,2]]
   fu=np.array([[349,1419],[628,1636],[959,1270]])
   res.extend(((project(c,fp)*1368/c['W']-fu)/8).ravel())
  res.append((x[i+5]-cameras[n]['C'][2])/.20)
  res.append((x[i+6]-math.log(cameras[n]['f']))/.15)
 return np.array(res)
lo=np.full(len(x0),-np.inf);hi=-lo
lo[0]=2.1;hi[0]=2.8
for n in names:
 i=1+names.index(n)*7;lo[i+5]=.6;hi[i+5]=2.1;lo[i+6]=math.log(cameras[n]['f']*.6);hi[i+6]=math.log(cameras[n]['f']*1.6)
fit=least_squares(residual,x0,bounds=(lo,hi),max_nfev=3000,loss='soft_l1',f_scale=3)
report={'revision':'T','window_height_m':fit.x[0],'plan_scale_m_per_pixel':1/35.2,'status':'architecture controls, approximate raster plan, not survey calibration','window_nodes_plan_pixels':plan_nodes,'cameras':{}}
for n in names:
 c=unpack(fit.x,n);p,uv=data(fit.x,n);pred=project(c,p)*1368/c['W'];err=np.linalg.norm(pred-uv,axis=1)
 c.update(revision='T',window_height_m=float(fit.x[0]),status='architecture-first fit with explicitly counted panes; raster plan dimensions approximate',architecture_controls={'world':p.tolist(),'pixels_1368':uv.tolist(),'predicted_1368':pred.tolist(),'residuals_1368_px':err.tolist()})
 (O/f'{n}_camera.json').write_text(json.dumps(c,indent=2),encoding='utf8');report['cameras'][n]={'C':c['C'],'f':c['f'],'errors_ref_px':err.tolist()}
 print(n,'C',np.round(c['C'],3),'f_ref',round(c['f']*1368/c['W'],2),'errors',np.round(err,1),flush=True)
 im=Image.open(R/f'images/photos/{n}.jpg').convert('RGB');im=im.resize((1368,round(im.height*1368/im.width)));d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
 for j,((k,z,u),q) in enumerate(zip(obs[n],pred)):
  d.line([tuple(u),tuple(q)],fill='#ff3030',width=3);d.ellipse((q[0]-7,q[1]-7,q[0]+7,q[1]+7),outline='#ff3030',width=3);d.ellipse((u[0]-5,u[1]-5,u[0]+5,u[1]+5),fill='#00ffff');d.text((u[0]+10,u[1]-25),f'D{k} '+('head' if z else 'sill'),font=font,fill='#00ffff',stroke_width=2,stroke_fill='black')
 # Common diagonal window projection across full frame, not a local crop.
 for k in range(len(xy)):
  q=project(c,[[*xy[k],0],[*xy[k],fit.x[0]]])*1368/c['W']
  if np.max(np.abs(q))<20000:d.line([tuple(v) for v in q],fill='#ff3030',width=2)
 for z in [0,fit.x[0]]:
  q=project(c,[[*v,z] for v in xy])*1368/c['W'];d.line([tuple(v) for v in q],fill='#ff3030',width=2)
 im.save(O/f'{n}_architecture_fit.jpg',quality=93)
print('height',fit.x[0],flush=True)
(O/'architecture_fit.json').write_text(json.dumps(report,indent=2),encoding='utf8')
