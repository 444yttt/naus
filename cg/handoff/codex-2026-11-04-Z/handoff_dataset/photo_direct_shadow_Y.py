"""Primary-light differential floor shadows. Separate from full-GI furniture radiance.

The photographed floor supplies its existing indirect illumination. This pass
estimates added primary-source occlusion without transporting an uncalibrated
room-proxy radiosity change across the whole plate. Contact AO is separate.
"""
from pathlib import Path
import bpy,sys,json
R=Path(__file__).resolve().parent;O=R/'out_Y';args=sys.argv[sys.argv.index('--')+1:];shot=args[0];preview='--preview' in args;mode='preview' if preview else 'full'
bpy.ops.wm.open_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));S=bpy.context.scene
S.render.use_border=False;S.render.use_crop_to_border=False;S.render.resolution_percentage=25 if preview else 50;S.render.threads=10;S.cycles.samples=48;S.cycles.adaptive_min_samples=16;S.cycles.use_denoising=True
S.cycles.max_bounces=1;S.cycles.diffuse_bounces=0;S.cycles.glossy_bounces=0;S.cycles.transmission_bounces=0
nn=S.node_tree.nodes;ll=S.node_tree.links;nn.clear();rl=nn.new('CompositorNodeRLayers');co=nn.new('CompositorNodeComposite');ll.new(rl.outputs['Image'],co.inputs[0]);fo=nn.new('CompositorNodeOutputFile');fo.format.file_format='OPEN_EXR_MULTILAYER';fo.format.color_depth='32'
while fo.inputs:fo.file_slots.remove(fo.inputs[0])
fo.file_slots.new('Shadow Catcher');ll.new(rl.outputs['Shadow Catcher'],fo.inputs['Shadow Catcher'])
static=('LDK_floor','TV_back_wall','Kitchen_wall','Hall_return','Kitchen_top_wall','Ceiling','Kitchen_cabinet','Kitchen_wall_counter','Existing_island','Sink','Faucet','Balcony_overhang','Balcony_reflection_photo','Diagonal_reflection_photo')
for state in ['','_empty']:
 if state:
  for ob in S.objects:
   if ob.type in ['MESH','CURVE'] and not ob.name.startswith(static):ob.hide_render=True
 fo.base_path=str(O/f'{shot}_{mode}_direct_shadow{state}_passes');S.render.filepath=str(O/f'{shot}_{mode}_direct_shadow{state}.png');bpy.ops.render.render(write_still=True);print('DIRECT_SHADOW',shot,mode,state or 'full',flush=True)
(O/f'{shot}_{mode}_direct_shadow_settings.json').write_text(json.dumps({'floor_shadow_transport':'primary light-source visibility only; diffuse/glossy/transmission bounces0, max1','furniture_radiance':'unchanged full12-bounce foreground render and full-GI floor-reflected furniture radiance','contact':'separate 100mm geometry AO, normalized against the empty room','reason':'avoid imposing unmeasured proxy-room higher-order irradiance changes on photographed remote floor; no photographic retouch or image-local correction','samples':48,'resolution_percentage':S.render.resolution_percentage,'limitation':'higher-order diffuse lighting changes on the photographed floor are not reconstructed; incoming illumination and BRDF are photo estimates, not measured HDR'},indent=2))
