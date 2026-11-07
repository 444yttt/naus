from pathlib import Path
import bpy
R=Path(__file__).resolve().parent;O=R/'out_Z/light_trials'
bpy.ops.wm.open_mainfile(filepath=str(R/'out_Z/light_trials/p09_initial_rug_scene.blend'));s=bpy.context.scene
s.render.resolution_percentage=25;s.render.threads=10;s.cycles.samples=24;s.cycles.adaptive_min_samples=16
for nd in list(s.node_tree.nodes):
    if nd.type=='OUTPUT_FILE':s.node_tree.nodes.remove(nd)
ma=bpy.data.materials['Shedir02_Burro_colour_study'];ao_mix=[n for n in ma.node_tree.nodes if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY' and n.inputs[2].is_linked and n.inputs[2].links[0].from_node.type=='AMBIENT_OCCLUSION']
for energy,ao in [(2000,.35),(300,0),(1000,0),(2000,0)]:
    s.objects['Diagonal_sky_bay_return_Y'].data.energy=energy
    for n in ao_mix:n.inputs[0].default_value=ao
    s.render.filepath=str(O/f'p09_balance_{energy}_{ao}.png');bpy.ops.render.render(write_still=True);print('BALANCE_TRIAL_DONE',energy,ao,flush=True)
