"""Lighting-only diagnostic, never overwrite common source scenes/native renders."""
from pathlib import Path
import bpy
R=Path(__file__).resolve().parent;O=R/'out_Z/light_trials';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'out_Z/light_trials/p09_initial_rug_scene.blend'));s=bpy.context.scene
s.render.resolution_percentage=25;s.render.threads=6;s.cycles.samples=24;s.cycles.adaptive_min_samples=16
for nd in list(s.node_tree.nodes):
    if nd.type=='OUTPUT_FILE':s.node_tree.nodes.remove(nd)
for energy in [300,600,1000]:
    s.objects['Diagonal_sky_bay_return_Y'].data.energy=energy
    s.render.filepath=str(O/f'p09_sky{energy}.png');bpy.ops.render.render(write_still=True);print('LIGHT_TRIAL_DONE',energy,flush=True)
