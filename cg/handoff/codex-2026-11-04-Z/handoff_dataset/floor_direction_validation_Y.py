from pathlib import Path
import json,cv2,numpy as np,math
from photo_common_X import floor_mask
R=Path(__file__).resolve().parent;O=R/'out_Y';rows=[]
for shot in ['u1','u2','p09','p01','p13']:
 cameras={k:json.loads((p/f'{shot}_camera.json').read_text()) for k,p in [('W',R/'out/photo_final_W'),('X',R/'out_X'),('Y',O)]};c=cameras['W'];sf=1600/c['W'];hh=round(c['H']*sf);im=cv2.resize(cv2.imread(str(R/f'images/photos_srgb/{shot}.png')),(1600,hh),interpolation=cv2.INTER_AREA);g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY);fm=floor_mask(shot,1600,hh)>.99;lines=cv2.createLineSegmentDetector().detect(g)[0];report={'shot':shot,'definition':'long original-photo floor segments, frozen using W camera direction; identical source segments compared for W/X/Y. May include timber grain, not surveyed floor markers.','axes':[]}
 for axis,minlen in [(0,65),(1,25)]:
  def vp(cam):
   q=np.array(cam['R'])[:,axis];return(q[:2]/q[2]*cam['f']+cam.get('principal_point_native_px',[cam['W']/2,cam['H']/2]))*sf
  oldvp=vp(c);chosen=[]
  if lines is not None:
   for line in lines.reshape(-1,4):
    a,b=line[:2],line[2:];mid=(a+b)/2;length=np.linalg.norm(b-a)
    if length<minlen:continue
    pix=np.rint([a,mid,b]).astype(int)
    if np.any(pix[:,0]<0) or np.any(pix[:,0]>=1600) or np.any(pix[:,1]<0) or np.any(pix[:,1]>=hh) or not np.all(fm[pix[:,1],pix[:,0]]):continue
    u=(b-a)/length;v=oldvp-mid;v/=np.linalg.norm(v);ang=np.rad2deg(np.arcsin(np.clip(abs(np.cross(u,v)),0,1)))
    if ang<=5:chosen.append((float(length),a.tolist(),b.tolist()))
  variants={}
  for version,cam in cameras.items():
   target=vp(cam);errs=[];angs=[]
   for length,a,b in chosen:
    a,b=np.array(a),np.array(b);u=(b-a)/length;v=target-(a+b)/2;v/=np.linalg.norm(v);sine=np.clip(abs(np.cross(u,v)),0,1);errs.append(.5*length*sine/sf);angs.append(np.rad2deg(np.arcsin(sine)))
   variants[version]={'endpoint_rms_native_px':float(np.sqrt(np.mean(np.array(errs)**2))) if errs else None,'median_angle_degrees':float(np.median(angs)) if angs else None,'source_segment_count':len(chosen)}
  report['axes'].append({'world_axis':'XY'[axis],'source_segments_at1600width':chosen,'measurements':variants})
 rows.append(report)
(O/'floor_direction_validation.json').write_text(json.dumps(rows,indent=2));print(json.dumps([{'shot':r['shot'],'axes':[{'axis':a['world_axis'],'measurements':a['measurements']} for a in r['axes']]} for r in rows],indent=2))
