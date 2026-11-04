from pathlib import Path
import bpy,sys
R=Path(__file__).resolve().parent;O=R/'out/photo_final_W';sys.path.insert(0,str(R))
bpy.ops.wm.open_mainfile(filepath=str(O/'u2_photo_scene.blend'));S=bpy.context.scene
from eames_cushions_W import rebuild
rebuild(S,R/'out/photo_final_V/u1_photo_scene.blend')
S.render.resolution_percentage=50;S.render.use_border=True;S.render.use_crop_to_border=True
S.render.border_min_x=.1;S.render.border_max_x=.26;S.render.border_min_y=.28;S.render.border_max_y=.52
S.render.threads=10;S.cycles.samples=24;S.cycles.adaptive_min_samples=8
for node in list(S.node_tree.nodes):
 if node.type=='OUTPUT_FILE':S.node_tree.nodes.remove(node)
S.render.filepath=str(O/'u2_back_skin_v2_test.png');bpy.ops.render.render(write_still=True)
