from pathlib import Path
import bpy,sys
R=Path(__file__).resolve().parent;O=R/'out_Y';args=sys.argv[sys.argv.index('--')+1:];shot=args[0];background='--background' in args;preview='--preview' in args
bpy.ops.wm.open_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));S=bpy.context.scene;mode='preview' if preview else 'full'
if preview:S.render.resolution_percentage=25
if background:
 static=('LDK_floor','TV_back_wall','Kitchen_wall','Hall_return','Kitchen_top_wall','Ceiling','Kitchen_cabinet','Kitchen_wall_counter','Existing_island','Sink','Faucet','Balcony_overhang','Balcony_reflection_photo','Diagonal_reflection_photo')
 for ob in S.objects:
  if ob.type in ['MESH','CURVE'] and not ob.name.startswith(static):ob.hide_render=True
 S.render.use_border=False;S.render.resolution_percentage=25 if preview else 50;S.cycles.samples=8;S.cycles.adaptive_min_samples=4
 S.render.filepath=str(O/f'{shot}_background_foreground.png')
 for node in S.node_tree.nodes:
  if node.type=='OUTPUT_FILE':node.base_path=str(O/f'{shot}_background_passes')
else:
 S.render.filepath=str(O/f'{shot}_{mode}_foreground.png')
 for node in S.node_tree.nodes:
  if node.type=='OUTPUT_FILE':node.base_path=str(O/f'{shot}_{mode}_passes')
bpy.ops.render.render(write_still=True)
print('Y_RENDERED',shot,'background' if background else mode,flush=True)
