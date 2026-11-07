import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'out/photo_final_V/u2_photo_scene.blend'))
rows=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and not o.name.startswith(('Ernest','TV_tile')):
  rows.append(dict(name=o.name,vertices=len(o.data.vertices),polygons=len(o.data.polygons),dimensions=list(o.dimensions),materials=[m.name for m in o.data.materials if m],smooth=sum(p.use_smooth for p in o.data.polygons),modifiers=[m.type for m in o.modifiers],minimum_z=min((o.matrix_world@v.co).z for v in o.data.vertices)))
(R/'out/audit_W.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
