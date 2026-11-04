"""Report comparable original AND independently refined observation errors."""
from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parent;O=R/'out_Z';controls=json.loads((R/'out_X/camera_fit_X.json').read_text());rows=[]
def project(c,P):
    q=(P-np.asarray(c['C']))@np.asarray(c['R']).T
    return q[:,:2]/q[:,2:]*c['f']+np.asarray(c.get('principal_point_native_px',[c['W']/2,c['H']/2]))
for shot in ['u1','u2','p09','p01','p13']:
    v=next(r for r in controls if r['shot']==shot);P=np.asarray(v['controls_world']);original=np.asarray(v['controls_observed_native_px']);z=json.loads((O/f'{shot}_camera.json').read_text());refined=np.asarray(z.get('refined_native_observations',original));per=[]
    for rev,folder in [('W',R/'out/photo_final_W'),('X',R/'out_X'),('Z',O)]:
        c=json.loads((folder/f'{shot}_camera.json').read_text());p=project(c,P)
        def stats(obs):
            e=np.linalg.norm(p-obs,axis=1);return {'rms_native_px':float(np.sqrt(np.mean(e*e))),'maximum_native_px':float(e.max()),'residual_norms_native_px':e.tolist()}
        per.append({'revision':rev,'original_observations':stats(original),'refined_observations':stats(refined)})
    rows.append({'shot':shot,'controls_world':P.tolist(),'controls_observed_native_px':original.tolist(),'controls_refined_native_px':refined.tolist(),'measurement_change':'u2/p13 island corners remeasured from original-photo line intersections; all controls and world geometry retained' if shot in ['u2','p13'] else 'original observations unchanged','comparison':per,'Z_improves_original_observation_RMS_vs_W':per[2]['original_observations']['rms_native_px']<per[0]['original_observations']['rms_native_px'],'Z_improves_refined_observation_RMS_vs_W':per[2]['refined_observations']['rms_native_px']<per[0]['refined_observations']['rms_native_px'],'target_7px_pass':per[2]['refined_observations']['rms_native_px']<=7,'camera_geometry_not_surveyed':True})
(O/'camera_fit_Z.json').write_text(json.dumps(rows,indent=2));print('Z_CAMERA_FIT',[(r['shot'],r['comparison'][0]['original_observations']['rms_native_px'],r['comparison'][2]['original_observations']['rms_native_px'],r['comparison'][2]['refined_observations']['rms_native_px']) for r in rows],flush=True)
