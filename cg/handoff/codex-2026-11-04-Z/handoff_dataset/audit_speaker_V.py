import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(R/'out/3d_R/Harajuku_LDK_R.blend'));out=[]
for root in bpy.data.objects:
 if root.name.startswith('Beolab28_OFFICIAL_'):
  vv=[root.matrix_world.inverted()@(o.matrix_world@v.co) for o in root.children if o.type=='MESH' for v in o.data.vertices];lo=[min(v[i] for v in vv) for i in range(3)];hi=[max(v[i] for v in vv) for i in range(3)];print(root.name,'root',list(root.location),'bounds_local',lo,hi,'children',[o.name for o in root.children]);out.append(dict(name=root.name,location=list(root.location),bounds_local=[lo,hi]))
(R/'out/speaker_source_audit.json').write_text(json.dumps(out,indent=2))
