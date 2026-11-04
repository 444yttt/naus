from pathlib import Path
import bpy,bmesh,json
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'out/photo_final_V/u1_photo_scene.blend'));ob=next(o for o in bpy.context.scene.objects if o.name.startswith('SEAT-FABRIC'))
bm=bmesh.new();bm.from_mesh(ob.data);unseen=set(bm.verts);rows=[]
while unseen:
 todo=[unseen.pop()];component=[]
 while todo:
  v=todo.pop();component.append(v)
  for e in v.link_edges:
   q=e.other_vert(v)
   if q in unseen:unseen.remove(q);todo.append(q)
 a=[list(v.co) for v in component];lo=[min(v[j] for v in a) for j in range(3)];hi=[max(v[j] for v in a) for j in range(3)]
 rows.append(dict(count=len(a),lo=lo,hi=hi))
print(json.dumps(sorted(rows,key=lambda a:-a['count']),indent=2))
