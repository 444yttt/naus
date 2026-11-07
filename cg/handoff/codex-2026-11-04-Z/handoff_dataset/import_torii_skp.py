from pathlib import Path
import sys,json,bpy,addon_utils
from mathutils import Vector
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r/'runtime/sketchup_addon'))
bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('sketchup_importer',default_set=True,persistent=False)
bpy.ops.import_scene.skp(filepath=str(r/'models/torii_user_warehouse/source.skp'),import_camera=False,scenes_as_camera=False,max_instance=999)
bpy.context.view_layer.update()
result=[]
for ob in bpy.data.objects:
 if ob.type=='MESH':
  pts=[ob.matrix_world@Vector(v) for v in ob.bound_box]
  result.append(dict(name=ob.name,verts=len(ob.data.vertices),lo=[min(p[i] for p in pts) for i in range(3)],hi=[max(p[i] for p in pts) for i in range(3)],materials=[m.name if m else None for m in ob.data.materials]))
print('IMPORT_RESULT',json.dumps(result,indent=2))
(r/'models/torii_user_warehouse/inspection.json').write_text(json.dumps(result,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(r/'models/torii_user_warehouse/source.blend'))
