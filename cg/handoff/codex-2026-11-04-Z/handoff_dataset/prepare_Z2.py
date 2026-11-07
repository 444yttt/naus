"""Z2 = Z common scene + two common changes, applied identically to all five view scenes:
1) Eames rear-opening sliver removal (fix_eames_Z2.py); 2) Ernest table grain finish (ernest_wood_Z2.py).
Cameras, lights, world, layout, rug and all other materials stay exactly as Z."""
from pathlib import Path
import bpy,json,sys
R=Path(__file__).resolve().parent;O=R/'out_Z2';O.mkdir(exist_ok=True);shot=sys.argv[sys.argv.index('--')+1]
sys.path.insert(0,str(R))
bpy.ops.wm.open_mainfile(filepath=str(R/f'out_Z/{shot}_photo_scene.blend'));S=bpy.context.scene
import fix_eames_Z2,ernest_wood_Z2
info={'shot':shot,'source':f'out_Z/{shot}_photo_scene.blend','eames':fix_eames_Z2.fix(S),'wood':ernest_wood_Z2.apply()}
for nd in S.node_tree.nodes:
    if nd.type=='OUTPUT_FILE':nd.base_path=str(O/f'{shot}_full_passes')
S.render.filepath=str(O/f'{shot}_full_foreground.png')
(O/f'{shot}_prepare_Z2.json').write_text(json.dumps(info,indent=2))
(O/f'{shot}_camera.json').write_text((R/f'out_Z/{shot}_camera.json').read_text())
bpy.ops.wm.save_as_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));print('Z2_PREPARED',json.dumps(info),flush=True)
