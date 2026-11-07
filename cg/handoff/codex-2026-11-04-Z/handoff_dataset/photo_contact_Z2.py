from pathlib import Path
import bpy,sys
R=Path(__file__).resolve().parent;O=R/'out_Z2';args=sys.argv[sys.argv.index('--')+1:];shot=args[0];preview='--preview' in args;mode='preview' if preview else 'full'
bpy.ops.wm.open_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));S=bpy.context.scene
for ob in S.objects:
 if ob.type in ['MESH','CURVE']:ob.visible_camera=ob.name in ['LDK_floor','Existing_island_plan_proxy'];ob.is_shadow_catcher=False
 if ob.type=='LIGHT':ob.data.energy=0
S.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
floor=bpy.data.objects['LDK_floor'];ma=bpy.data.materials.new('Geometry_contact_AO_100mm');ma.use_nodes=True;nn=ma.node_tree.nodes;ll=ma.node_tree.links;nn.clear()
ao=nn.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=.10;ao.samples=32;em=nn.new('ShaderNodeEmission');ou=nn.new('ShaderNodeOutputMaterial');ll.new(ao.outputs['AO'],em.inputs['Color']);ll.new(em.outputs[0],ou.inputs['Surface']);floor.data.materials.clear();floor.data.materials.append(ma)
island=bpy.data.objects['Existing_island_plan_proxy'];island.data.materials.clear();island.data.materials.append(ma)
S.render.use_border=False;S.render.use_crop_to_border=False
S.render.resolution_percentage=25 if preview else 50;S.render.threads=10;S.cycles.samples=24;S.cycles.adaptive_min_samples=8;S.cycles.use_denoising=True
nn=S.node_tree.nodes;ll=S.node_tree.links;nn.clear();rl=nn.new('CompositorNodeRLayers');co=nn.new('CompositorNodeComposite');ll.new(rl.outputs['Image'],co.inputs[0]);fo=nn.new('CompositorNodeOutputFile');fo.base_path=str(O/f'{shot}_{mode}_contact_AO_passes');fo.format.file_format='OPEN_EXR_MULTILAYER';fo.format.color_depth='16'
while fo.inputs:fo.file_slots.remove(fo.inputs[0])
fo.file_slots.new('Image');ll.new(rl.outputs['Image'],fo.inputs['Image']);S.render.filepath=str(O/f'{shot}_{mode}_contact_AO.png');bpy.ops.render.render(write_still=True)
# Normalize the existing room's own occlusion out of the contact layer. The plate
# already contains its wall/cabinet shadows; only added furniture should darken it.
static=('LDK_floor','TV_back_wall','Kitchen_wall','Hall_return','Kitchen_top_wall','Ceiling','Kitchen_cabinet','Kitchen_wall_counter','Existing_island','Sink','Faucet','Balcony_overhang','Balcony_reflection_photo','Diagonal_reflection_photo')
for ob in S.objects:
 if ob.type in ['MESH','CURVE'] and not ob.name.startswith(static):ob.hide_render=True
fo.base_path=str(O/f'{shot}_{mode}_contact_AO_empty_passes');S.render.filepath=str(O/f'{shot}_{mode}_contact_AO_empty.png');S.cycles.samples=8;bpy.ops.render.render(write_still=True)
print('CONTACT_COMPLETE',shot,mode,flush=True)
