from pathlib import Path
import bpy,json,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parent;O=R/'out_Y/shadow_audit';O.mkdir(exist_ok=True)
allprobes={}
for version,folder in [('W',R/'out/photo_final_W'),('Y',R/'out_Y')]:
 bpy.ops.wm.open_mainfile(filepath=str(folder/'u2_photo_scene.blend'));S=bpy.context.scene
 eames=[ob for ob in S.objects if ob.type=='MESH' and ob.name.startswith('SEAT-')]
 deps=bpy.context.evaluated_depsgraph_get();probes=[];sun=S.objects.get('Sun_estimated_from_floor_shadows');sunward=-(sun.rotation_euler.to_matrix()@Vector((0,0,-1)))
 for ix in range(45):
  x=1.9+(ix-22)*.04
  for iy in range(45):
   y=1.85+(iy-22)*.04;r=math.hypot(x-1.9,y-1.85)
   if not .40<=r<=.88:continue
   p=Vector((x,y,.002));d=p-S.camera.matrix_world.translation;hit,loc,no,face,ob,mat=S.ray_cast(deps,S.camera.matrix_world.translation,d.normalized(),distance=d.length+.03)
   if not hit or ob.name!='LDK_floor' or (loc-p).length>.04:continue
   q=world_to_camera_view(S,S.camera,p)
   if not(0<q.x<1 and 0<q.y<1):continue
   h,lo,n,f,obj,ma=S.ray_cast(deps,p,sunward,distance=20)
   probes.append({'world':[x,y,0.],'uv_normalized':[q.x,1-q.y],'sun_first_hit':obj.name if h else None,'sun_blocked_by_Eames':h and obj.name.startswith('SEAT-')})
 allprobes[version]=probes
 S.render.use_border=False;S.render.resolution_percentage=25;S.render.threads=6;S.cycles.samples=24;S.cycles.adaptive_min_samples=24;S.cycles.adaptive_threshold=.01
 nn=S.node_tree.nodes;ll=S.node_tree.links;nn.clear();rl=nn.new('CompositorNodeRLayers');co=nn.new('CompositorNodeComposite');ll.new(rl.outputs['Image'],co.inputs[0]);fo=nn.new('CompositorNodeOutputFile');fo.format.file_format='OPEN_EXR_MULTILAYER';fo.format.color_depth='32'
 while fo.inputs:fo.file_slots.remove(fo.inputs[0])
 fo.file_slots.new('Shadow Catcher');ll.new(rl.outputs['Shadow Catcher'],fo.inputs['Shadow Catcher'])
 for mode in ['all','no_Eames']:
  for ob in eames:ob.hide_render=mode=='no_Eames'
  fo.base_path=str(O/f'u2_{version}_{mode}_passes');S.render.filepath=str(O/f'u2_{version}_{mode}.png');bpy.ops.render.render(write_still=True);print('SHADOW_ISOLATION',version,mode,flush=True)
(O/'world_floor_probes.json').write_text(json.dumps({'definition':'fixed physical annulus 0.40 to0.88m around Eames centre(1.9,1.85); .04m world grid, visibility tested against unchanged geometry, not selected by output colour or render agreement','probes':allprobes},indent=2))
