"""Cross-view warm floor-return balance with chosen material, diagnostics only."""
from pathlib import Path
import bpy
R=Path(__file__).resolve().parent;O=R/'out_Z/light_trials'
for shot in ['u1','p09']:
    bpy.ops.wm.open_mainfile(filepath=str(R/f'out_Z/{shot}_photo_scene.blend'));s=bpy.context.scene
    s.render.resolution_percentage=25;s.render.threads=10;s.cycles.samples=24;s.cycles.adaptive_min_samples=16
    for nd in list(s.node_tree.nodes):
        if nd.type=='OUTPUT_FILE':s.node_tree.nodes.remove(nd)
    s.objects['Sunlit_balcony_floor_return_Y'].data.energy=350
    s.render.filepath=str(O/f'{shot}_sheen45_warm350.png');bpy.ops.render.render(write_still=True);print('WARM_BALANCE_DONE',shot,flush=True)
