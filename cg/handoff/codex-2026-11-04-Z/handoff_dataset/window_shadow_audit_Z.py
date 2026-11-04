"""Photo-derived balcony profile positions; no production scene mutation."""
from pathlib import Path
import json,cv2,numpy as np
R=Path(__file__).resolve().parent;O=R/'out_Z';rows=[]
for shot,roi in [('p09',(0,1450,1880,2600)),('u1',(2600,1400,4284,3650))]:
    c=json.loads((O/f'{shot}_camera.json').read_text());im=cv2.imread(str(R/f'images/photos_srgb/{shot}.png'));x0,y0,x1,y1=roi;crop=im[y0:y1,x0:x1];gray=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY);lines=cv2.createLineSegmentDetector().detect(gray)[0]
    K=np.array([[c['f'],0,c.get('principal_point_native_px',[c['W']/2,c['H']/2])[0]],[0,c['f'],c.get('principal_point_native_px',[c['W']/2,c['H']/2])[1]],[0,0,1.]])
    rr=[]
    for raw in lines.reshape(-1,4):
        a,b=raw[:2]+[x0,y0],raw[2:]+[x0,y0];v=b-a;length=float(np.linalg.norm(v))
        if length<250 or abs(v[0])>abs(v[1])*.1:continue
        l=np.cross(np.r_[a,1],np.r_[b,1]);l/=np.linalg.norm(l[:2]);n=np.asarray(c['R']).T@K.T@l
        if abs(n[2])/np.linalg.norm(n)>.025 or abs(n[0])<1e-8:continue
        X=float(c['C'][0]+n[1]/n[0]*c['C'][1])
        if not -.1<X<9.6:continue
        rr.append({'segment_native_px':[a.tolist(),b.tolist()],'length_px':length,'implied_world_x_at_balcony_y0':X,'vertical_plane_normal_Z_fraction':float(abs(n[2])/np.linalg.norm(n))})
    rr.sort(key=lambda x:x['implied_world_x_at_balcony_y0']);rows.append({'shot':shot,'ROI':roi,'segments':rr,'scope':'LSD candidates only; may include curtain/door edges; no frame width or shadow fit claimed'})
(O/'window_shadow_photo_audit.json').write_text(json.dumps(rows,indent=2));print('BALCONY_PROFILE_CANDIDATES',[(r['shot'],[(round(v['implied_world_x_at_balcony_y0'],3),round(v['length_px'])) for v in r['segments']]) for r in rows])
