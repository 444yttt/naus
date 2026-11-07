import bpy,json,hashlib,array,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R/'out_Z2';before=json.loads((R/'out_X/before_snapshot.json').read_text());rows=[]
for shot in ['u1','u2','p09','p01','p13']:
 bpy.ops.wm.open_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));S=bpy.context.scene
 moved=[];unexpected=[];lightdiff=[]
 for name,old in before[shot]['objects'].items():
  ob=S.objects.get(name)
  if ob is None:unexpected.append({'object':name,'missing':True});continue
  delta=max(abs(ob.matrix_world[j][k]-old['matrix_world'][j][k]) for j in range(4) for k in range(4))
  if delta>1e-6:
   if ob.type=='CAMERA' and shot in ['u2','p13']:continue
   parent=ob
   while parent.parent:parent=parent.parent
   if parent.name=='Linha_Dining_THIRDPARTY_260' or parent.name.startswith('Torii_USER_MODEL_'):moved.append(name)
   else:unexpected.append({'object':name,'matrix_max_delta':delta})
  if ob.type=='LIGHT':
   if abs(ob.data.energy-old['energy'])>1e-6 or max(abs(a-b) for a,b in zip(ob.data.color,old['color']))>1e-6:lightdiff.append(name)
 cam=S.camera;old=before[shot]['objects'][before[shot]['camera']]
 cd=max(abs(cam.matrix_world[j][k]-old['matrix_world'][j][k]) for j in range(4) for k in range(4));cd=max(cd,abs(cam.data.lens-old['lens']),abs(cam.data.shift_x-old['shift_x']),abs(cam.data.shift_y-old['shift_y']))
 c=next(o for o in S.objects if o.name.startswith('SEAT-FABRIC'));co=array.array('f',[0])*(3*len(c.data.vertices));c.data.vertices.foreach_get('co',co);gh=hashlib.sha256(co.tobytes()).hexdigest()
 # For quantitative face comparisons, world-space representative surface centres.
 probes=[]
 for ob in S.objects:
  if ob.pass_index!=8 or ob.type!='MESH':continue
  for pi in range(0,len(ob.data.polygons),max(1,len(ob.data.polygons)//500)):
   poly=ob.data.polygons[pi]
   n=(ob.matrix_world.to_3x3().inverted().transposed()@poly.normal).normalized();p=ob.matrix_world@poly.center
   if max(abs(v) for v in n)<.9:continue
   probes.append({'world':list(p),'normal':list(n),'object':ob.name})
 joint=[];a=Vector((3.8352272727,6.9034090909));b=Vector((4.8295454545,6.5625));t=(b-a).normalized();n=Vector((-t.y,t.x));deps=bpy.context.evaluated_depsgraph_get()
 from bpy_extras.object_utils import world_to_camera_view
 for along in [-.3,-.15,0,.15,.3]:
  for z in [.746,.76,.79,.82]:
   xy=(a+b)/2+t*along-n*.0001;p=Vector((xy.x,xy.y,z));di=p-cam.location;hit,loc,normal,index,ob,mat=S.ray_cast(deps,cam.location,di.normalized(),distance=di.length+.02)
   uv=world_to_camera_view(S,cam,p)
   if hit and ob.name.startswith('Existing_island') and uv.z>0 and 0<uv.x<1 and 0<uv.y<1:joint.append([uv.x*S.render.resolution_x,(1-uv.y)*S.render.resolution_y])
 row={'shot':shot,'allowed_moved_meshes_and_roots':moved,'unexpected_pose_changes':unexpected,'existing_light_changes':lightdiff,'new_lights':[o.name for o in S.objects if o.type=='LIGHT' and o.name not in before[shot]['objects']],'camera_max_numeric_difference':cd,'eames_cushion_sha256':gh,'sofa_surface_probes':probes,'visible_island_joint_test_pixels':joint}
 row['actual_lights']={o.name:{'energy_W_or_sun_strength':o.data.energy,'colour_RGB':list(o.data.color),'position_m':list(o.location),'rotation_rad':list(o.rotation_euler),'size_m':getattr(o.data,'size',None)} for o in S.objects if o.type=='LIGHT'}
 row['actual_materials']={}
 for ma in bpy.data.materials:
  if not ma.use_nodes or not ma.name.startswith(('Shedir02_Burro_colour_study','Eames_dark_wood_refined')):continue
  bs=ma.node_tree.nodes.get('Principled BSDF')
  if bs:
   row['actual_materials'][ma.name]={k:list(bs.inputs[k].default_value) if hasattr(bs.inputs[k].default_value,'__len__') else bs.inputs[k].default_value for k in ['Base Color','Roughness','Sheen Weight','Coat Weight','Coat Roughness']}
   row['actual_materials'][ma.name]['base_colour_linked']=bool(bs.inputs['Base Color'].links)
   row['actual_materials'][ma.name]['AO_nodes']=[{'name':v.name,'distance_m':v.inputs['Distance'].default_value,'only_local':v.only_local} for v in ma.node_tree.nodes if v.type=='AMBIENT_OCCLUSION']
 bg=S.world.node_tree.nodes.get('Background');row['world_X']={'colour':list(bg.inputs['Color'].default_value),'strength':bg.inputs['Strength'].default_value}
 rows.append(row)
 assert not unexpected and not lightdiff,(shot,unexpected,lightdiff)
 if shot not in ['u2','p13']:assert cd==0,(shot,cd)
 bpy.ops.wm.open_mainfile(filepath=str(R/'out/photo_final_W'/f'{shot}_photo_scene.blend'));bg=bpy.context.scene.world.node_tree.nodes.get('Background');row['world_W']={'colour':list(bg.inputs['Color'].default_value),'strength':bg.inputs['Strength'].default_value};assert row['world_X']==row['world_W']
(O/'scene_delta_Z2.json').write_text(json.dumps(rows,indent=2));print('SCENE_DELTA_CHECKED',[(r['shot'],r['camera_max_numeric_difference']) for r in rows])
