from pathlib import Path
import bpy,json,sys
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_U';rows=[]
for shot in ['n01','n02','n03','n04','u2','p01']:
 bpy.ops.wm.open_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));S=bpy.context.scene
 rugs=[ob.name for ob in S.objects if 'shindo' in ob.name.lower()]
 c=S.camera;manifest=[]
 prefixes=('Ernest','ERNEST','Torii','TORII','Linha','LINHA','Eames','EAMES','Beolab','Beosound','TV97','IVRESSE','Ivresse')
 for ob in S.objects:
  if ob.type!='MESH' or not ob.name.startswith(prefixes):continue
  q=[world_to_camera_view(S,c,ob.matrix_world@Vector(v)) for v in ob.bound_box];q=[v for v in q if v.z>0]
  if not q:continue
  xs=[v.x for v in q];ys=[v.y for v in q];manifest.append(dict(name=ob.name,bbox_normalized_bottom_origin=[min(xs),min(ys),max(xs),max(ys)],in_frame=not(max(xs)<0 or min(xs)>1 or max(ys)<0 or min(ys)>1),hidden=ob.hide_render))
 row=dict(shot=shot,full_frame=not S.render.use_border,percentage=S.render.resolution_percentage,source_width=S.render.resolution_x,source_height=S.render.resolution_y,rug_objects=rugs,camera_matrix=[list(v) for v in c.matrix_world],objects=manifest)
 assert row['full_frame'] and not rugs
 rows.append(row)
(O/'scene_full_frame_QA.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print('U_FULL_FRAME_NO_RUG_SCENE_QA_PASS',flush=True)
