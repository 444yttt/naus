import bpy,json
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(Path('handoff_dataset/models/ernest_tables_mesmetric/3d/Poliform-ERNEST-coffeetable-1.fbx').resolve()))
bpy.context.view_layer.update()
out=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
  out.append(dict(name=o.name,vertices=len(o.data.vertices),lo=lo,hi=hi,materials=[m.name if m else None for m in o.data.materials]))
p=Path('handoff_dataset/models/ernest_tables_mesmetric/inspection.json');p.write_text(json.dumps(out,indent=2))
print('MESHES',len(out));print(json.dumps(out[:12],indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(Path('handoff_dataset/models/ernest_tables_mesmetric/source.blend').resolve()))
