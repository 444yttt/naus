from pathlib import Path
import bpy,sys,json
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R/'out_Y';shot=sys.argv[sys.argv.index('--')+1]
for label,power in [('return200',200),('return500',500),('return900',900)]:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'out_X/{shot}_photo_scene.blend'));S=bpy.context.scene
 ld=bpy.data.lights.new('Sunlit_balcony_floor_return_Y','AREA');ld.energy=power;ld.color=(1,.72,.32);ld.shape='RECTANGLE';ld.size=9.0;ld.size_y=.6;ld.specular_factor=0
 ob=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(ob);ob.location=(4.7,-.10,.22);ob.rotation_euler=(Vector((4.7,2,.60))-ob.location).to_track_quat('-Z','Y').to_euler();ob.visible_glossy=False
 ma=bpy.data.materials['Ernest_dark_wood_study'];bs=ma.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.22;bs.inputs['Coat Weight'].default_value=.20;bs.inputs['Coat Roughness'].default_value=.16
 for n in bpy.data.materials['Shedir02_Burro_colour_study'].node_tree.nodes:
  if n.type=='AMBIENT_OCCLUSION':n.inputs['Distance'].default_value=.025
  if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY' and n.inputs[2].is_linked and n.inputs[2].links[0].from_node.type=='AMBIENT_OCCLUSION':n.inputs[0].default_value=.35
 S.render.resolution_percentage=25;S.render.use_border=False;S.render.threads=10;S.cycles.samples=24;S.render.filepath=str(O/f'{shot}_{label}_foreground.png')
 for nd in S.node_tree.nodes:
  if nd.type=='OUTPUT_FILE':nd.base_path=str(O/f'{shot}_{label}_passes')
 bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(O/f'{shot}_{label}_scene.blend'));print('RETURN_TRIAL',shot,label,flush=True)
