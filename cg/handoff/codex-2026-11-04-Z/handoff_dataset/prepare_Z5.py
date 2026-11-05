from pathlib import Path
import bpy,json,sys
R=Path(__file__).resolve().parent;O=R/'out_Z5';O.mkdir(exist_ok=True);shot=sys.argv[sys.argv.index('--')+1];sys.path.insert(0,str(R))
bpy.ops.wm.open_mainfile(filepath=str(R/f'out_Z4/{shot}_photo_scene.blend'));S=bpy.context.scene
import add_props_Z5;log=add_props_Z5.apply(S)
for nd in S.node_tree.nodes:
    if nd.type=='OUTPUT_FILE':nd.base_path=str(O/f'{shot}_full_passes')
S.render.filepath=str(O/f'{shot}_full_foreground.png')
(O/f'{shot}_camera.json').write_text((R/f'out_Z4/{shot}_camera.json').read_text());(O/f'{shot}_prepare_Z5.json').write_text(json.dumps(log,indent=2,default=str))
bpy.ops.wm.save_as_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));print('Z5_PREPARED',shot,flush=True)
