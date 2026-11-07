from pathlib import Path
import json,cv2,numpy as np
from photo_common_X import floor_mask
R=Path(__file__).resolve().parent;O=R/'out_Z2';rows=[]
for scene in json.loads((O/'scene_inspection.json').read_text()):
    shot=scene['shot'];W,H=scene['native_size'];mask=floor_mask(shot,W,H)
    coverage=cv2.imread(str(O/f'{shot}_full_reflection_coverage.png'),0).astype('float32')/255
    objects={}
    for c in scene['visible_floor_contact_candidates']:
        x,y=[round(v) for v in c['pixel']]
        if not 0<=x<W or not 0<=y<H:continue
        r=max(4,round(W/500));patch=coverage[max(0,y-r):min(H,y+r+1),max(0,x-r):min(W,x+r+1)]
        px,py,pz=c['world_m'];on_rug=5.2<=px<=8.7 and .35<=py<=4.35;nearby=bool(patch.max()>.03)
        group=objects.setdefault(c['object'],{'contacts':0,'outside_floor_mask':0,'with_nearby_reflection':0,'minimum_mask':1.,'contacts_on_rug':0,'contacts_on_exposed_floor':0,'exposed_floor_with_nearby_reflection':0})
        group['contacts']+=1;group['outside_floor_mask']+=int(mask[y,x]<.5);group['with_nearby_reflection']+=int(nearby);group['minimum_mask']=min(group['minimum_mask'],float(mask[y,x]))
        group['contacts_on_rug']+=int(on_rug);group['contacts_on_exposed_floor']+=int(not on_rug);group['exposed_floor_with_nearby_reflection']+=int(not on_rug and nearby)
    rows.append({'shot':shot,'objects':objects,'method':'visible 3D contact candidates versus receiver mask; exposed-floor candidates require nearby physical mirror coverage; contacts inside opaque Shindo footprint do not require reflected feet. Includes compression of thin pile under unchanged feet, not a fabric dynamics simulation.'})
(O/'delivery/details').mkdir(parents=True,exist_ok=True)
(O/'delivery/details/contact_coverage.json').write_text(json.dumps(rows,indent=2))
print('Z_CONTACT_COVERAGE',[(r['shot'],sum(v['outside_floor_mask'] for v in r['objects'].values()),sum(v['contacts_on_rug'] for v in r['objects'].values()),sum(v['contacts_on_exposed_floor']-v['exposed_floor_with_nearby_reflection'] for v in r['objects'].values())) for r in rows])
