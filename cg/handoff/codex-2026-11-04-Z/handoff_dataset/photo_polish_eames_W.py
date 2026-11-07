from pathlib import Path
import bpy,sys,json,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parent;O=R/'out/photo_final_W';sys.path.insert(0,str(R));shot=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.open_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));S=bpy.context.scene;cloth=next(o for o in S.objects if o.name.startswith('SEAT-FABRIC'))
asset=O/'Eames_cushion_surfaces_W_v2.blend';materials=list(cloth.data.materials)
if asset.exists():
 with bpy.data.libraries.load(str(asset),link=False) as (src,dst):dst.meshes=[n for n in src.meshes if n.startswith('Eames_five_closed_cushions')]
 cloth.modifiers.clear();cloth.data=dst.meshes[0];cloth.data.materials.clear()
 for m in materials:cloth.data.materials.append(m)
else:
 from eames_cushions_W import rebuild
 cloth=rebuild(S,R/'out/photo_final_V/u1_photo_scene.blend')
 bpy.data.libraries.write(str(asset),{cloth.data},fake_user=True,compress=True)
cloth['closed_cushion_repair']='five original component envelopes; interpolated visible surfaces; timber-covered rear skin omitted; fine relief simplified'
S.render.resolution_percentage=100;S.render.use_border=False;S.render.use_crop_to_border=False
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'))
W,H=S.render.resolution_x,S.render.resolution_y;points=[]
for ob in S.objects:
 if ob.type=='MESH' and ob.name.startswith('SEAT-'):
  for corner in ob.bound_box:
   q=world_to_camera_view(S,S.camera,ob.matrix_world@Vector(corner))
   if q.z>.05:points.append(q)
visible=bool(points) and max(q.x for q in points)>0 and min(q.x for q in points)<1 and max(q.y for q in points)>0 and min(q.y for q in points)<1
record={'shot':shot,'surface_version':2,'visible_roi':visible,'original_cushion_bounds_preserved':True,'repair':'five original component envelopes; smoothly interpolated visible surfaces; timber-covered rear skin omitted; fine relief simplified; feet unchanged'}
if visible:
 x0=max(0,min(q.x for q in points)-.06);x1=min(1,max(q.x for q in points)+.06);y1=min(1,max(q.y for q in points)+.035)
 S.render.use_border=True;S.render.use_crop_to_border=True;S.render.border_min_x=x0;S.render.border_max_x=x1;S.render.border_min_y=0;S.render.border_max_y=y1
 x=int(S.render.border_min_x*W);right=int(S.render.border_max_x*W);top=H-int(S.render.border_max_y*H)
 record.update(x=x,y=top,width=right-x,height=H-top)
 S.render.threads=10;S.cycles.samples=24;S.cycles.adaptive_min_samples=8;S.cycles.adaptive_threshold=.02
 S.render.filepath=str(O/f'{shot}_polish_foreground.png')
 for node in S.node_tree.nodes:
  if node.type=='OUTPUT_FILE':node.base_path=str(O/f'{shot}_polish_passes')
 (O/f'{shot}_polish_roi.json').write_text(json.dumps(record,indent=2))
 bpy.ops.render.render(write_still=True)
else:(O/f'{shot}_polish_roi.json').write_text(json.dumps(record,indent=2))
print('EAMES_POLISH_RENDERED',shot,record,flush=True)
