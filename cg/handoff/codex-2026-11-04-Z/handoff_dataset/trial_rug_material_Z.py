"""Compare restrained leather-like response without modifying colour or geometry."""
from pathlib import Path
import bpy
R=Path(__file__).resolve().parent;O=R/'out_Z/light_trials'
bpy.ops.wm.open_mainfile(filepath=str(R/'out_Z/light_trials/p09_initial_rug_scene.blend'));s=bpy.context.scene
s.render.resolution_percentage=25;s.render.threads=10;s.cycles.samples=24;s.cycles.adaptive_min_samples=16
for nd in list(s.node_tree.nodes):
    if nd.type=='OUTPUT_FILE':s.node_tree.nodes.remove(nd)
b=bpy.data.materials['Shedir02_Burro_colour_study'].node_tree.nodes.get('Principled BSDF')
for label,coat,rough in [('sheen0coat05',.05,.46),('sheen0coat0',0,.46),('sheen0coat05rough2',.05,.2),('sheen0coat0rough2',0,.2)]:
    b.inputs['Sheen Weight'].default_value=0;b.inputs['Coat Weight'].default_value=coat;b.inputs['Roughness'].default_value=rough
    s.render.filepath=str(O/f'p09_material_{label}.png');bpy.ops.render.render(write_still=True);print('MATERIAL_TRIAL_DONE',label,flush=True)
