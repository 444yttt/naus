from pathlib import Path
import bpy
R=Path(__file__).resolve().parent;O=R/'out/photo_final_W'
bpy.ops.wm.open_mainfile(filepath=str(O/'u1_photo_scene.blend'));S=bpy.context.scene
import sys
sys.path.insert(0,str(R))
from eames_cushions_W import rebuild
rebuild(S,R/'out/photo_final_V/u1_photo_scene.blend')
S.render.resolution_percentage=100;S.render.use_border=True;S.render.use_crop_to_border=True
S.render.border_min_x=.40;S.render.border_max_x=.59;S.render.border_min_y=.11;S.render.border_max_y=.23
S.render.threads=4;S.cycles.samples=16;S.cycles.adaptive_min_samples=4
for n in list(S.node_tree.nodes):
 if n.type=='OUTPUT_FILE':S.node_tree.nodes.remove(n)
S.render.filepath=str(O/'u1_eames_polish_test.png');bpy.ops.render.render(write_still=True)
