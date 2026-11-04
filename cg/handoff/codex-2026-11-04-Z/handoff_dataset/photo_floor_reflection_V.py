"""Physical new-furniture floor reflection and dielectric opacity.
Existing proxies return black to glossy rays, so their uncalibrated reflections never replace the plate.
"""
from pathlib import Path
import sys,bpy,json
R=Path(__file__).resolve().parent;O=R/'out/photo_final_V';shot=sys.argv[sys.argv.index('--')+1];preview='--preview' in sys.argv;only_occlusion='--occlusion-only' in sys.argv;modeprefix='preview' if preview else 'full'
bpy.ops.wm.open_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));S=bpy.context.scene
# Replace packed source-card pixels with ICC-converted sRGB textures.
for ob in S.objects:
 if ob.name.startswith(('Balcony_reflection_photo','Diagonal_reflection_photo')):
  for slot in ob.material_slots:
   if slot.material and slot.material.use_nodes:
    for node in slot.material.node_tree.nodes:
     if node.type=='TEX_IMAGE' and node.image:
      path=R/'images/photos_srgb'/(Path(node.image.filepath).stem+'.png')
      if path.exists():node.image=bpy.data.images.load(str(path),check_existing=True)
S.render.threads=10;S.cycles.samples=32;S.cycles.use_denoising=True;S.render.resolution_percentage=25 if preview else 50;S.render.use_border=False
static=('LDK_floor','TV_back_wall','Kitchen_wall','Hall_return','Kitchen_top_wall','Ceiling','Kitchen_cabinet','Kitchen_wall_counter','Existing_island','Sink','Faucet','Balcony_overhang','Balcony_reflection_photo','Diagonal_reflection_photo')
added=[];added_hidden={};card_materials=[]
original_world_colour=tuple(S.world.node_tree.nodes['Background'].inputs['Color'].default_value)
original_world_strength=S.world.node_tree.nodes['Background'].inputs['Strength'].default_value
for ob in S.objects:
 if ob.type not in ['MESH','CURVE']:continue
 ob.visible_camera=ob.name=='LDK_floor';ob.is_shadow_catcher=False
 if ob.name=='LDK_floor':continue
 if not ob.name.startswith(static):added.append(ob);added_hidden[ob.name]=ob.hide_render;continue
 if ob.name.startswith(('Balcony_reflection_photo','Diagonal_reflection_photo')):card_materials.append((ob,[slot.material for slot in ob.material_slots]))
 # Preserve ordinary diffuse bounce/occlusion but suppress proxy radiance on glossy paths.
 for slot in ob.material_slots:
  if not slot.material:continue
  ma=slot.material.copy();ma.use_nodes=True;nn=ma.node_tree.nodes;ll=ma.node_tree.links;ou=next(n for n in nn if n.type=='OUTPUT_MATERIAL');old=ou.inputs['Surface'].links[0].from_socket if ou.inputs['Surface'].links else None
  if old is None:continue
  lp=nn.new('ShaderNodeLightPath');black=nn.new('ShaderNodeBsdfDiffuse');black.inputs['Color'].default_value=(0,0,0,1);mix=nn.new('ShaderNodeMixShader');ll.new(lp.outputs['Is Glossy Ray'],mix.inputs[0]);ll.new(old,mix.inputs[1]);ll.new(black.outputs[0],mix.inputs[2]);ll.new(mix.outputs[0],ou.inputs['Surface']);slot.material=ma
floor=bpy.data.objects['LDK_floor'];ma=bpy.data.materials.new('Floor_dielectric_new_objects_only');ma.use_nodes=True;bs=ma.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(0,0,0,1);bs.inputs['Roughness'].default_value=.19;bs.inputs['IOR'].default_value=1.5;bs.inputs['Coat Weight'].default_value=.20;bs.inputs['Coat Roughness'].default_value=.16;floor.data.materials.clear();floor.data.materials.append(ma)
n=S.node_tree.nodes;l=S.node_tree.links;n.clear();rl=n.new('CompositorNodeRLayers');co=n.new('CompositorNodeComposite');l.new(rl.outputs['Image'],co.inputs[0]);fo=n.new('CompositorNodeOutputFile');fo.format.file_format='OPEN_EXR_MULTILAYER';fo.format.color_depth='16'
while fo.inputs:fo.file_slots.remove(fo.inputs[0])
fo.file_slots.new('Image');l.new(rl.outputs['Image'],fo.inputs['Image'])
for mode in (['environment','environment_occluded'] if only_occlusion else ['furniture','opacity','environment','environment_occluded','white_reference']):
 S.cycles.samples=8 if mode=='white_reference' else 24 if mode=='opacity' else 32
 if mode=='opacity':
  em=bpy.data.materials.new('Reflection_opacity_unit_emission');em.use_nodes=True;em.cycles.emission_sampling='NONE';nn=em.node_tree.nodes;nn.clear();e=nn.new('ShaderNodeEmission');e.inputs[0].default_value=(1,1,1,1);e.inputs[1].default_value=1;ou=nn.new('ShaderNodeOutputMaterial');em.node_tree.links.new(e.outputs[0],ou.inputs['Surface'])
  for ob in added:
   ob.data.materials.clear();ob.data.materials.append(em)
  for ob in S.objects:
   if ob.type=='LIGHT':ob.data.energy=0
  S.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
 if mode=='environment':
  for ob in S.objects:
   if ob.type=='LIGHT':ob.data.energy=0
  for ob in added:ob.hide_render=True
  for ob,mats in card_materials:
   for slot,ma in zip(ob.material_slots,mats):slot.material=ma
  S.world.node_tree.nodes['Background'].inputs['Color'].default_value=original_world_colour
  S.world.node_tree.nodes['Background'].inputs['Strength'].default_value=original_world_strength
 if mode=='environment_occluded':
  black=bpy.data.materials.new('New_furniture_environment_occluder');black.use_nodes=True;nn=black.node_tree.nodes;nn.clear();b=nn.new('ShaderNodeBsdfDiffuse');b.inputs['Color'].default_value=(0,0,0,1);ou=nn.new('ShaderNodeOutputMaterial');black.node_tree.links.new(b.outputs[0],ou.inputs['Surface'])
  for ob in added:
   ob.hide_render=added_hidden[ob.name];ob.data.materials.clear();ob.data.materials.append(black)
 if mode=='white_reference':
  for ob in S.objects:
   if ob.type in ['MESH','CURVE'] and ob.name!='LDK_floor':ob.hide_render=True
  S.world.node_tree.nodes['Background'].inputs['Color'].default_value=(1,1,1,1)
  S.world.node_tree.nodes['Background'].inputs['Strength'].default_value=1
 if only_occlusion and mode=='environment':continue
 fo.base_path=str(O/f'{shot}_{modeprefix}_floor_reflection_{mode}_passes');S.render.filepath=str(O/f'{shot}_{modeprefix}_floor_reflection_{mode}.png');bpy.ops.render.render(write_still=True)
(O/f'{shot}_{modeprefix}_floor_reflection_settings.json').write_text(json.dumps({'mode':modeprefix,'resolution_percentage':S.render.resolution_percentage,'samples_by_pass':{'furniture':32,'opacity':24,'environment':32,'environment_occluded':32,'white_reference':8},'source_size':[S.render.resolution_x,S.render.resolution_y],'physical_floor_reflection':True,'roughness':.19,'coat_roughness':.16,'IOR':1.5,'method':'five-pass glossy response: new furniture radiance, weighted coverage, photographic environment before/after new-object occlusion, unit-white BRDF; directional radiance loss where photometrically aligned, unweighted coverage fallback; diffuse shadow separated','status':'photo-estimated BRDF; not measured'},indent=2))
