import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent
p=r/'models/eames_official/source.blend'
bpy.ops.wm.open_mainfile(filepath=str(p))
for ob in list(bpy.data.objects):
 if ob.type!='MESH':bpy.data.objects.remove(ob,do_unlink=True);continue
 ob.data.transform(ob.matrix_world.copy());ob.parent=None;ob.matrix_world.identity()
 bm=bmesh.new();bm.from_mesh(ob.data)
 # Ottoman is spatially separate in the manufacturer's combined SKP.
 cut=[v for v in bm.verts if v.co.x>1.05]
 bmesh.ops.delete(bm,geom=cut,context='VERTS');bm.to_mesh(ob.data);bm.free();ob.data.update()
 if not len(ob.data.vertices):bpy.data.objects.remove(ob,do_unlink=True)
bpy.context.view_layer.update()
pts=[v.co for ob in bpy.data.objects if ob.type=='MESH' for v in ob.data.vertices]
lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
print('CHAIR_LOCAL_BOUNDS',lo,hi,'SIZE',[hi[i]-lo[i] for i in range(3)])
(r/'models/eames_official/chair_dimensions.json').write_text(json.dumps(dict(lo=lo,hi=hi),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(r/'models/eames_official/chair_only.blend'))
