from pathlib import Path
import json,numpy as np,cv2
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parent;O=R/'out_Y';rows=json.loads((R/'out_X/camera_fit_X.json').read_text());shot='p13'
im=cv2.imread(str(R/f'images/photos_srgb/{shot}.png'))
def segments(rect):
 x,y,w,h=rect;v=cv2.createLineSegmentDetector().detect(cv2.cvtColor(im[y:y+h,x:x+w],cv2.COLOR_BGR2GRAY))[0].reshape(-1,4);v+=np.array([x,y,x,y]);return v
def tls(lines):
 pts=np.asarray(lines).reshape(-1,2);v=cv2.fitLine(pts,cv2.DIST_L2,0,.001,.001).reshape(-1);dx,dy,x,y=v;return np.array([-dy,dx,dy*x-dx*y],dtype='float64')
def cross(a,b):
 q=np.cross(a,b);return q[:2]/q[2]
far=segments((1680,2090,500,240));right=segments((2010,2160,150,210))
# Segment sets selected from original-photo edge crops (not camera projections).
# Pick by audited endpoint coordinates rather than unstable detector sequence IDs.
def near(pool,examples):
 found=[]
 for e in examples:
  e=np.array(e);ds=np.minimum(np.linalg.norm(pool-e,axis=1),np.linalg.norm(pool-e[[2,3,0,1]],axis=1));found.append(pool[np.argmin(ds)])
 return found
left=tls(near(far,[[1808,2216,1760,2223],[1952,2192,1907,2199],[1759,2224,1712,2231],[1869,2206,1828,2212]]))
back=tls(near(right,[[2091,2201,2037,2198]]))
side=tls(near(right,[[2125,2286,2121,2266],[2122,2265,2111,2203]]))
front=tls(near(right,[[2085,2304,2116,2293],[2010,2328,2085,2304]]))
refined={5:cross(side,front),6:cross(side,back),7:cross(left,back)}
row=next(r for r in rows if r['shot']==shot);c=json.loads((R/f'out_X/{shot}_camera.json').read_text());P=np.array(row['controls_world']);uv=np.array(row['controls_observed_native_px']);old=uv.copy()
for i,v in refined.items():uv[i]=v
rv=Rotation.from_matrix(c['R']).as_rotvec();x0=np.r_[rv,c['C'],np.log(c['f']),(np.array(c['principal_point_native_px'])-[c['W']/2,c['H']/2])/c['W'],0.]
def project(x):
 q=(P-x[3:6])@Rotation.from_rotvec(x[:3]).as_matrix().T;a=q[:,:2]/q[:,2:];a*=1+x[9]*(a*a).sum(1)[:,None];return a*np.exp(x[6])+[c['W']/2,c['H']/2]+x[7:9]*c['W']
lo=np.r_[rv-.15,np.array(c['C'])-1,np.log(c['f']*.7),-.05,-.05,-.12];hi=np.r_[rv+.15,np.array(c['C'])+1,np.log(c['f']*1.3),.05,.05,.12]
fit=least_squares(lambda x:(project(x)-uv).ravel(),x0,bounds=(lo,hi),max_nfev=5000,xtol=1e-12,ftol=1e-12,gtol=1e-12);err=np.linalg.norm(project(fit.x)-uv,axis=1)
result={'shot':shot,'world_controls_unchanged':P.tolist(),'observations_original':old.tolist(),'observations_native_edge_refined':uv.tolist(),'refined_ids':list(refined),'measurement_method':'Native original-photo straight-edge intersections at three island top corners. No geometry fitting, no deleted observations, no background warp. Original annotations retained. Camera estimates not used to select edge pixels.','edge_lines':{k:v.tolist() for k,v in [('left',left),('back',back),('side',side),('front',front)]},'radial_k1_estimate':float(fit.x[9]),'rms_refined':float(np.sqrt((err**2).mean())),'max_refined':float(err.max()),'residuals_refined':err.tolist(),'parameters':fit.x.tolist(),'old_camera_rms_against_refined_observations':float(np.sqrt(np.mean(np.sum((project(x0)-uv)**2,axis=1)))),'status':'diagnostic pending full edge validation'}
(O/'native_edge_radial_camera_p13.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['world_controls_unchanged','parameters','edge_lines']},indent=2))
for i in refined:
 a=old[i];b=uv[i];cv2.line(im,tuple(np.rint(a).astype(int)),tuple(np.rint(b).astype(int)),(0,0,255),2);cv2.drawMarker(im,tuple(np.rint(b).astype(int)),(0,255,255),cv2.MARKER_CROSS,14,1)
cv2.imwrite(str(O/'p13_native_corner_refinement.png'),im[2100:2370,1700:2200])
