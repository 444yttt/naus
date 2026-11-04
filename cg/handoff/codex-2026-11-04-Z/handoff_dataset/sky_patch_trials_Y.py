from pathlib import Path
import bpy,sys
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R/'out_Y';shot=sys.argv[sys.argv.index('--')+1]
for label,power in [('sky150',150),('sky300',300)]:
 bpy.ops.wm.open_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));S=bpy.context.scene
 ld=bpy.data.lights.new('Diagonal_sky_bay_return_Y','AREA');ld.energy=power;ld.color=(.65,.82,1);ld.shape='RECTANGLE';ld.size=3;ld.size_y=2.2;ld.specular_factor=0
 ob=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(ob);ob.location=(1.55,4.54,1.45);ob.rotation_euler=(Vector((6.25,3.8,.65))-ob.location).to_track_quat('-Z','Y').to_euler();ob.visible_glossy=False
 S.render.resolution_percentage=25;S.render.use_border=False;S.render.threads=6;S.cycles.samples=24;S.render.filepath=str(O/f'{shot}_{label}_foreground.png')
 for nd in S.node_tree.nodes:
  if nd.type=='OUTPUT_FILE':nd.base_path=str(O/f'{shot}_{label}_passes')
 bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(O/f'{shot}_{label}_scene.blend'));print('SKY_PATCH_TRIAL',shot,label,flush=True)
