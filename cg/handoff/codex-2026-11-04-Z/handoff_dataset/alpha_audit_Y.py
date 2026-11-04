from pathlib import Path
import bpy,sys,json
R=Path(__file__).resolve().parent;O=R/'out_Y';shot=sys.argv[sys.argv.index('--')+1];bpy.ops.wm.open_mainfile(filepath=str(R/f'out_X/{shot}_photo_scene.blend'));S=bpy.context.scene
static=('LDK_floor','TV_back_wall','Kitchen_wall','Hall_return','Kitchen_top_wall','Ceiling','Kitchen_cabinet','Kitchen_wall_counter','Existing_island','Sink','Faucet','Balcony_overhang','Balcony_reflection_photo','Diagonal_reflection_photo')
ma=bpy.data.materials.new('MATTE_UNIT');ma.use_nodes=True;nn=ma.node_tree.nodes;nn.clear();e=nn.new('ShaderNodeEmission');e.inputs[0].default_value=(1,1,1,1);ou=nn.new('ShaderNodeOutputMaterial');ma.node_tree.links.new(e.outputs[0],ou.inputs['Surface'])
materials={};obinfo={}
for ob in S.objects:
 if ob.type=='LIGHT':ob.data.energy=0
 if ob.type not in ['MESH','CURVE']:continue
 obinfo[ob.name]={'camera':ob.visible_camera,'shadowcatcher':ob.is_shadow_catcher,'holdout':ob.is_holdout}
 if ob.name.startswith('Ernest_DEALER_FBX_table'):
  for sl in ob.material_slots:
   if sl.material and sl.material.use_nodes:materials[sl.material.name]=[{'name':n.name,'type':n.type,'inputs':{i.name:list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value for i in n.inputs if hasattr(i,'default_value') and (isinstance(i.default_value,(float,int)) or hasattr(i.default_value,'__len__'))}} for n in sl.material.node_tree.nodes]
 if ob.name.startswith(static):
  ob.is_shadow_catcher=False;ob.is_holdout=ob.visible_camera
 else:
  ob.is_shadow_catcher=False;ob.is_holdout=False;ob.data.materials.clear();ob.data.materials.append(ma)
S.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0;S.render.resolution_percentage=25;S.render.threads=10;S.cycles.samples=16;S.render.use_border=False
for n in list(S.node_tree.nodes):
 if n.type=='OUTPUT_FILE':S.node_tree.nodes.remove(n)
S.render.filepath=str(O/f'{shot}_true_object_matte.png');bpy.ops.render.render(write_still=True)
(O/f'{shot}_alpha_audit_scene.json').write_text(json.dumps({'objects':obinfo,'coffee_materials':materials},indent=2))
print('ALPHA_AUDIT_RENDERED',shot)
