from pathlib import Path
import bpy,json,sys,math
from mathutils import Vector,Matrix,Quaternion
R=Path(__file__).resolve().parent;O=R/'out_Y';shot=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.open_mainfile(filepath=str(R/f'out_X/{shot}_photo_scene.blend'));S=bpy.context.scene
# Preserve all original light objects and the world. Add a common estimated
# sunlit-balcony return, not a camera-specific fill or a photograph adjustment.
ld=bpy.data.lights.new('Sunlit_balcony_floor_return_Y','AREA');ld.energy=200;ld.color=(1,.72,.32);ld.shape='RECTANGLE';ld.size=9;ld.size_y=.6;ld.specular_factor=0
ob=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(ob);ob.location=(4.7,-.10,.22);ob.rotation_euler=(Vector((4.7,2,.60))-ob.location).to_track_quat('-Z','Y').to_euler();ob.visible_glossy=False
ld=bpy.data.lights.new('Diagonal_sky_bay_return_Y','AREA');ld.energy=300;ld.color=(.65,.82,1);ld.shape='RECTANGLE';ld.size=3;ld.size_y=2.2;ld.specular_factor=0
ob=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(ob);ob.location=(1.55,4.54,1.45);ob.rotation_euler=Vector((.937,-.349,0)).to_track_quat('-Z','Y').to_euler();ob.visible_glossy=False
ma=bpy.data.materials['Ernest_dark_wood_study'];bs=ma.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.22;bs.inputs['Coat Weight'].default_value=.20;bs.inputs['Coat Roughness'].default_value=.16
for nd in ma.node_tree.nodes:
 if nd.type=='BUMP':nd.inputs['Distance'].default_value=.00012
ma.pass_index=10
for n in bpy.data.materials['Shedir02_Burro_colour_study'].node_tree.nodes:
 if n.type=='AMBIENT_OCCLUSION':n.inputs['Distance'].default_value=.025
 if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY' and n.inputs[2].is_linked and n.inputs[2].links[0].from_node.type=='AMBIENT_OCCLUSION':n.inputs[0].default_value=.35
c=json.loads((R/f'out_X/{shot}_camera.json').read_text())
if shot in ['u2','p13']:
 if shot=='p13':
  d=json.loads((O/'native_edge_camera_p13.json').read_text());v=d['parameters'];obs=d['observations_native_edge_refined'];rms=d['rms_refined']
 else:
  d=json.loads((O/'native_edge_camera_u2.json').read_text())[0];v=d['parameters'];obs=d['observations_refined'];rms=d['rms']
 axis=Vector(v[:3]);rot=Quaternion(axis.normalized(),axis.length).to_matrix()
 c.update(R=[list(z) for z in rot],C=v[3:6],f=math.exp(v[6]),principal_point_native_px=[c['W']/2+v[7]*c['W'],c['H']/2+v[8]*c['W']],revision='Y',status='pinhole refit after independent native-photo island edge measurements; unchanged approximate architecture geometry',refined_native_observations=obs,refined_native_rms_px=rms,measurement_audit=d)
 cam=S.camera;cam.matrix_world=Matrix.Translation(c['C'])@(rot.transposed()@Matrix(((1,0,0),(0,-1,0),(0,0,-1)))).to_4x4();cam.data.lens=c['f']*36/c['W'];cam.data.sensor_width=36;cam.data.sensor_fit='HORIZONTAL';cx,cy=c['principal_point_native_px'];cam.data.shift_x=-(cx-c['W']/2)/c['W'];cam.data.shift_y=(cy-c['H']/2)/c['W']
 bpy.context.view_layer.update()
(O/f'{shot}_camera.json').write_text(json.dumps(c,indent=2))
S.view_layers[0].use_pass_position=True;S.view_layers[0].use_pass_normal=True;S.view_layers[0].use_pass_material_index=True;S.view_layers[0].use_pass_object_index=True
rl=next(nd for nd in S.node_tree.nodes if nd.type=='R_LAYERS')
for nd in S.node_tree.nodes:
 if nd.type=='OUTPUT_FILE':
  nd.base_path=str(O/f'{shot}_full_passes')
  for key in ['Position','Normal','IndexMA','IndexOB']:
   if key not in nd.inputs:nd.file_slots.new(key)
   S.node_tree.links.new(rl.outputs[key],nd.inputs[key])
S.render.filepath=str(O/f'{shot}_full_foreground.png');S.render.threads=10;S.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));print('Y_PREPARED',shot,flush=True)
