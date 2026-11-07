from pathlib import Path
import bpy,json,sys
R=Path(__file__).resolve().parent;O=R/'out_Z6';O.mkdir(exist_ok=True);shot=sys.argv[sys.argv.index('--')+1];sys.path.insert(0,str(R))
bpy.ops.wm.open_mainfile(filepath=str(R/f'out_Z5/{shot}_photo_scene.blend'));S=bpy.context.scene
import plants_Z6;log=plants_Z6.apply(S)
bpy.ops.file.pack_all()
for nd in S.node_tree.nodes:
    if nd.type=='OUTPUT_FILE':nd.base_path=str(O/f'{shot}_full_passes')
S.render.filepath=str(O/f'{shot}_full_foreground.png')
(O/f'{shot}_camera.json').write_text((R/f'out_Z5/{shot}_camera.json').read_text());(O/f'{shot}_prepare_Z6.json').write_text(json.dumps(log,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));print('Z6_PREPARED',shot,json.dumps(log),flush=True)
