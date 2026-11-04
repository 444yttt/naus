from pathlib import Path
import json,cv2,numpy as np
import math
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_S'
pts=json.loads((O/'model_floor_contacts.json').read_text())['contacts'];P=np.array([p['point'] for p in pts])
layout=json.loads((R/'out/layout_Q.json').read_text(encoding='utf-8-sig'))
envelopes=[]
for it in layout['items']+layout['chairs']['items']:
 if 'center' not in it or 'size' not in it or len(it['size'])<2 or it.get('id')=='tv':continue
 w,d=it['size'][:2];angle=math.radians(it.get('angle',70.7));cs,sn=math.cos(angle),math.sin(angle);cx,cy=it['center']
 xy=[[-w/2,-d/2],[w/2,-d/2],[w/2,d/2],[-w/2,d/2]]
 envelopes.append(np.array([[cx+cs*x-sn*y,cy+sn*x+cs*y,0] for x,y in xy]))
for shot in ['u1','u2','p09','p01','p13']:
 c=json.loads((O/f'{shot}_camera.json').read_text());file=O/f'{shot}_full_composite.jpg'
 if not file.exists():file=R/f'images/photos/{shot}.jpg'
 im=cv2.imread(str(file));W,H=c['W'],c['H'];scale=1600/W;im=cv2.resize(im,(1600,round(H*scale)))
 for env in envelopes:
  v=(env-c['C'])@np.array(c['R']).T
  if np.any(v[:,2]<.01):continue
  p=(v[:,:2]/v[:,2:]*c['f']+[W/2,H/2])*scale
  if np.max(abs(p))<1e5:
   for a,b in zip(p,np.roll(p,-1,axis=0)):cv2.line(im,tuple(np.rint(a).astype(int)),tuple(np.rint(b).astype(int)),(0,165,255),2)
 q=(P-c['C'])@np.array(c['R']).T;uv=(q[:,:2]/q[:,2:]*c['f']+[W/2,H/2])*scale
 count=0
 for i,(p,z) in enumerate(zip(uv,q[:,2])):
  if z>.01 and 0<=p[0]<im.shape[1] and 0<=p[1]<im.shape[0]:cv2.circle(im,tuple(np.rint(p).astype(int)),5,(0,0,255),-1);count+=1
 cv2.putText(im,f'{shot}: projected 3D model floor contacts ({count}; includes hidden feet)',(30,45),cv2.FONT_HERSHEY_SIMPLEX,.8,(255,255,255),2)
 cv2.imwrite(str(O/f'{shot}_contacts_check.jpg'),im,[cv2.IMWRITE_JPEG_QUALITY,94])
print('CONTACT_OVERLAYS_SAVED')
