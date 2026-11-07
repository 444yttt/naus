import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.collada_import(filepath=str(r/'models/linha_warehouse/extracted/model.dae'))
bpy.context.view_layer.update()
out=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  ps=[o.matrix_world@Vector(p) for p in o.bound_box]
  out.append(dict(name=o.name,verts=len(o.data.vertices),lo=[min(p[i] for p in ps) for i in range(3)],hi=[max(p[i] for p in ps) for i in range(3)],materials=[m.name if m else None for m in o.data.materials]))
print('OBJECTS',len(out));print(json.dumps(out[:20],indent=2))
(r/'models/linha_warehouse/inspection.json').write_text(json.dumps(out,indent=2),encoding='utf8')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(r/'models/linha_warehouse/source.blend'))
