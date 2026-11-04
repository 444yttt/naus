from pathlib import Path
import bpy,json,sys
R=Path(__file__).resolve().parent;O=R/'out_Y';shot=sys.argv[sys.argv.index('--')+1]
variants=[('balanced',{'balcony':700,'diagonal':400,'sun':2.5})]
for label,cfg in variants:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'out_X/{shot}_photo_scene.blend'));S=bpy.context.scene
 lights=[]
 for ob in S.objects:
  if ob.type!='LIGHT':continue
  lights.append({'name':ob.name,'energy':ob.data.energy,'colour':list(ob.data.color),'location':list(ob.location),'specular':ob.data.specular_factor,'glossy':ob.visible_glossy})
  if cfg:
   if 'Balcony' in ob.name:
    ob.data.energy=cfg['balcony'];ob.data.color=(1,.97,.90);ob.data.specular_factor=1;ob.visible_glossy=True
   elif 'Diagonal' in ob.name:
    ob.data.energy=cfg['diagonal'];ob.data.color=(.80,.90,1.);ob.data.specular_factor=1;ob.visible_glossy=True
   elif ob.data.type=='SUN':ob.data.energy=cfg['sun']
   elif 'low_green' in ob.name:ob.data.energy=250;ob.data.color=(.95,1,.65)
 if cfg:
  S.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.09
  ma=bpy.data.materials['Ernest_dark_wood_study'];bs=ma.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.28;bs.inputs['Coat Weight'].default_value=.12;bs.inputs['Coat Roughness'].default_value=.22
  ma=bpy.data.materials['Shedir02_Burro_colour_study'];nn=ma.node_tree.nodes
  for n in nn:
   if n.type=='AMBIENT_OCCLUSION':n.inputs['Distance'].default_value=.025
   if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY' and n.inputs[2].is_linked and n.inputs[2].links[0].from_node.type=='AMBIENT_OCCLUSION':n.inputs[0].default_value=.35
 S.render.resolution_percentage=25;S.cycles.samples=24;S.render.threads=10;S.render.use_border=False
 S.render.filepath=str(O/f'{shot}_{label}_foreground.png')
 for nd in S.node_tree.nodes:
  if nd.type=='OUTPUT_FILE':nd.base_path=str(O/f'{shot}_{label}_passes')
 (O/f'{shot}_{label}_settings.json').write_text(json.dumps({'baseline_lights':lights,'changes':cfg},indent=2))
 bpy.ops.render.render(write_still=True)
 if cfg:bpy.ops.wm.save_as_mainfile(filepath=str(O/f'{shot}_{label}_scene.blend'))
 print('TRIAL_READY',shot,label,flush=True)
