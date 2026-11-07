"""Presentation see-through for n03 (user request): same scene without the Linha table and Torii
chairs, rendered through the same pipeline; the composite blends it only inside the marked area."""
from pathlib import Path
import bpy,sys
R=Path(__file__).resolve().parent;O=R/'out_Z6g';shot='n03'
bpy.ops.wm.open_mainfile(filepath=str(R/'out_Z6/n03_photo_scene.blend'));S=bpy.context.scene
hidden=[]
for o in S.objects:
    r=o
    while r.parent:r=r.parent
    if o.type=='MESH' and (r.name.startswith(('Linha_Dining','Torii_USER_MODEL')) or o.name.startswith(('Linha_','Flatware_Z5','Dining_lamp_Z5','Plate_Z5')) or 'TORII' in o.name.upper()):o.hide_render=True;hidden.append(o.name)
for nd in S.node_tree.nodes:
    if nd.type=='OUTPUT_FILE':nd.base_path=str(O/f'{shot}_full_passes')
S.render.filepath=str(O/f'{shot}_full_foreground.png')
(O/'n03_camera.json').write_text((R/'out_Z6/n03_camera.json').read_text());(O/'hidden_objects.txt').write_text('\n'.join(hidden))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'n03_photo_scene.blend'));print('GHOST_PREPARED',len(hidden))
