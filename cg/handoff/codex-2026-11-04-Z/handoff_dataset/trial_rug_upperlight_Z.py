"""Estimated upper-glazing sky contribution; diagnostics only."""
from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R/'out_Z/light_trials';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'out_Z/light_trials/p09_initial_rug_scene.blend'));s=bpy.context.scene
s.render.resolution_percentage=25;s.render.threads=10;s.cycles.samples=24;s.cycles.adaptive_min_samples=16
for nd in list(s.node_tree.nodes):
    if nd.type=='OUTPUT_FILE':s.node_tree.nodes.remove(nd)
ld=bpy.data.lights.new('Upper_glazing_sky_trial','AREA');ld.shape='RECTANGLE';ld.size=3;ld.size_y=.3;ld.color=(.65,.82,1);ld.specular_factor=0
ob=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(ob);ob.location=(1.55,4.54,2.45);ob.rotation_euler=(Vector((6.3,2.35,.6))-ob.location).to_track_quat('-Z','Y').to_euler();ob.visible_glossy=False
for energy in [200,400,800]:
    ld.energy=energy;s.render.filepath=str(O/f'p09_upper{energy}.png');bpy.ops.render.render(write_still=True);print('UPPER_LIGHT_TRIAL_DONE',energy,flush=True)
