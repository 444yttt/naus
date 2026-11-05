"""Z4 = Z3 (Z2 common scene; n03/n04 per-photo camera/sun/frame) with the Ernest tables' finish
replaced by ernest_wood_Z4. Nothing else changes."""
from pathlib import Path
import bpy,json,sys
R=Path(__file__).resolve().parent;O=R/'out_Z4';shot=sys.argv[sys.argv.index('--')+1];sys.path.insert(0,str(R))
src=R/('out_Z3' if shot.startswith('n') else 'out_Z2')/f'{shot}_photo_scene.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));S=bpy.context.scene
import ernest_wood_Z4,ernest_wood_Z2
old=bpy.data.materials['Ernest_dark_wood_grain_Z2'];ma=ernest_wood_Z4.build();n=0
for name in ernest_wood_Z2.TARGETS:
    for s in bpy.data.objects[name].material_slots:
        if s.material==old:s.material=ma;n+=1
for nd in S.node_tree.nodes:
    if nd.type=='OUTPUT_FILE':nd.base_path=str(O/f'{shot}_full_passes')
S.render.filepath=str(O/f'{shot}_full_foreground.png')
srcdir=src.parent
(O/f'{shot}_camera.json').write_text((srcdir/f'{shot}_camera.json').read_text())
(O/f'{shot}_prepare_Z4.json').write_text(json.dumps({'shot':shot,'source':str(src.relative_to(R)),'slots_replaced':n,'params':ernest_wood_Z4.P,'base_rgb':ernest_wood_Z4.BASE},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));print('Z4_PREPARED',shot,n,flush=True)
