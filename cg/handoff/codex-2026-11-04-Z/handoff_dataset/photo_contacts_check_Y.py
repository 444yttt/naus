from pathlib import Path
import json,cv2,numpy as np
from photo_common_X import floor_mask
R=Path(__file__).resolve().parent;O=R/'out_Y';rows=[]
for scene in json.loads((O/'scene_inspection.json').read_text()):
 shot=scene['shot'];W,H=scene['native_size'];mask=floor_mask(shot,W,H)
 coverage=cv2.imread(str(O/f'{shot}_full_reflection_coverage.png'),cv2.IMREAD_GRAYSCALE).astype('float32')/255
 objects={}
 for c in scene['visible_floor_contact_candidates']:
  x,y=[round(v) for v in c['pixel']]
  if not 0<=x<W or not 0<=y<H:continue
  r=max(4,round(W/500));patch=coverage[max(0,y-r):min(H,y+r+1),max(0,x-r):min(W,x+r+1)]
  group=objects.setdefault(c['object'],{'contacts':0,'outside_floor_mask':0,'with_nearby_reflection':0,'minimum_mask':1.})
  group['contacts']+=1;group['outside_floor_mask']+=int(mask[y,x]<.5);group['with_nearby_reflection']+=int(patch.max()>.03);group['minimum_mask']=min(group['minimum_mask'],float(mask[y,x]))
 rows.append({'shot':shot,'objects':objects,'method':'visible 3D floor contacts compared with photo receiver mask and rendered physical reflection coverage within a small pixel radius; this checks coverage, not an independent camera survey'})
(O/'delivery/details').mkdir(parents=True,exist_ok=True)
(O/'delivery/details/contact_coverage.json').write_text(json.dumps(rows,indent=2))
print('CONTACT_COVERAGE',[(r['shot'],sum(v['outside_floor_mask'] for v in r['objects'].values()),sum(v['contacts'] for v in r['objects'].values())) for r in rows])
