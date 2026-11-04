"""Independent check: Blender's actual camera equals the reported pinhole."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parent;O=R/'out_Z2';controls=json.loads((R/'out_X/camera_fit_X.json').read_text());rows=[]
for shot in ['u1','u2','p09','p01','p13']:
    bpy.ops.wm.open_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));s=bpy.context.scene
    c=json.loads((O/f'{shot}_camera.json').read_text());points=next(v for v in controls if v['shot']==shot)['controls_world'];errors=[]
    for p in points:
        a=world_to_camera_view(s,s.camera,Vector(p));blender=[a.x*c['W'],(1-a.y)*c['H']]
        q=[sum(c['R'][i][j]*(p[j]-c['C'][j]) for j in range(3)) for i in range(3)]
        pp=c.get('principal_point_native_px',[c['W']/2,c['H']/2]);reported=[q[0]/q[2]*c['f']+pp[0],q[1]/q[2]*c['f']+pp[1]]
        errors.append(math.dist(blender,reported))
    rows.append({'shot':shot,'controls':len(points),'maximum_report_vs_Blender_projection_difference_native_px':max(errors),'pass_within_0_05_px':max(errors)<.05,'meaning':'internal reproduction of calibrated camera; not external architectural accuracy'})
assert all(v['pass_within_0_05_px'] for v in rows),rows
(O/'camera_projection_consistency.json').write_text(json.dumps(rows,indent=2));print('CAMERA_PROJECTION_CHECK',rows,flush=True)
