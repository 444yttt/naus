"""Compare restrained leather-like response without modifying colour or geometry."""
from pathlib import Path
import bpy
R=Path(__file__).resolve().parent;O=R/'out_Z/light_trials'
bpy.ops.wm.open_mainfile(filepath=str(R/'out_Z/light_trials/p09_initial_rug_scene.blend'));s=bpy.context.scene
s.render.resolution_percentage=25;s.render.threads=10;s.cycles.samples=24;s.cycles.adaptive_min_samples=16
for nd in list(s.node_tree.nodes):
    if nd.type=='OUTPUT_FILE':s.node_tree.nodes.remove(nd)
b=bpy.data.materials['Shedir02_Burro_colour_study'].node_tree.nodes.get('Principled BSDF')
for label,coat,rough in [('sheen25',.13,.46),('sheen45',.13,.46),('rough85',.13,.85)]:
    b.inputs['Sheen Weight'].default_value=.25 if label=='sheen25' else .45 if label=='sheen45' else .1;b.inputs['Coat Weight'].default_value=coat;b.inputs['Roughness'].default_value=rough
    s.render.filepath=str(O/f'p09_material_{label}.png');bpy.ops.render.render(write_still=True);print('MATERIAL_TRIAL_DONE',label,flush=True)
