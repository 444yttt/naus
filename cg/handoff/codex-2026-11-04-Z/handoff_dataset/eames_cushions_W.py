"""Repair the five pad envelopes; omit rear skin concealed by the original wood."""
import bpy,bmesh
from mathutils import Vector
def rebuild(scene,source):
 cloth=next(o for o in scene.objects if o.name.startswith('SEAT-FABRIC'))
 materials=list(cloth.data.materials)
 with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('SEAT-FABRIC')]
 ref=dst.objects[0];bm=bmesh.new();bm.from_mesh(ref.data);unseen=set(bm.verts);components=[]
 while unseen:
  start=min(unseen,key=lambda v:v.index);unseen.remove(start);todo=[start];part=[];partverts=[]
  while todo:
   v=todo.pop();part.append(v.co.copy());partverts.append(v)
   for edge in v.link_edges:
    q=edge.other_vert(v)
    if q in unseen:unseen.remove(q);todo.append(q)
  idx={v:i for i,v in enumerate(partverts)};faces={f for v in partverts for f in v.link_faces}
  components.append((part,[tuple(idx[v] for v in f.verts) for f in faces]))
 bm.free();allverts=[];allfaces=[]
 for points,sourcefaces in sorted(components,key=lambda p:sum(v.z for v in p[0])/len(p[0])):
  hull=bmesh.new();vv=[hull.verts.new(p) for p in sorted(points,key=lambda p:tuple(p))];bmesh.ops.convex_hull(hull,input=vv,use_existing_faces=False)
  bmesh.ops.delete(hull,geom=[v for v in hull.verts if not v.link_faces],context='VERTS')
  bmesh.ops.join_triangles(hull,faces=list(hull.faces),angle_face_threshold=.55,angle_shape_threshold=.7)
  bmesh.ops.recalc_face_normals(hull,faces=list(hull.faces));me=bpy.data.meshes.new('Closed_cushion');hull.to_mesh(me);hull.free()
  tmp=bpy.data.objects.new('Cushion_interpolation_temp',me);scene.collection.objects.link(tmp)
  su=tmp.modifiers.new('Smooth supplied cushion envelope','SUBSURF');su.levels=3;su.render_levels=3
  ev=tmp.evaluated_get(bpy.context.evaluated_depsgraph_get());smooth=bpy.data.meshes.new_from_object(ev)
  lo=Vector(tuple(min(p[j] for p in points) for j in range(3)));hi=Vector(tuple(max(p[j] for p in points) for j in range(3)))
  a=Vector(tuple(min(v.co[j] for v in smooth.vertices) for j in range(3)));b=Vector(tuple(max(v.co[j] for v in smooth.vertices) for j in range(3)))
  offset=len(allverts)
  for v in smooth.vertices:
   p=Vector(tuple(lo[j]+(v.co[j]-a[j])*(hi[j]-lo[j])/max(b[j]-a[j],1e-8) for j in range(3)))
   allverts.append(tuple(p))
  for p in smooth.polygons:
   # These pads are backed by the supplied plywood shells. Artificial closing
   # faces intersected that timber; omit the concealed rear/bottom skin, exactly
   # as a multi-material upholstery assembly, preserving rounded visible rims.
   if lo.z<.2 and (p.normal.z<-.10 or p.normal.x<-.20):continue
   if lo.x<-.25 and lo.z>.2 and p.normal.x<-.10:continue
   allfaces.append(tuple(offset+i for i in p.vertices))
  bpy.data.objects.remove(tmp,do_unlink=True)
 result=bpy.data.meshes.new('Eames_five_closed_cushions_original_envelopes');result.from_pydata(allverts,[],allfaces);result.update()
 for m in materials:result.materials.append(m)
 cloth.modifiers.clear();cloth.data=result
 for p in result.polygons:p.use_smooth=True
 cloth['closed_cushion_repair']='original five component envelopes; smooth visible rims; wood-covered rear skin omitted'
 bpy.data.objects.remove(ref,do_unlink=True)
 return cloth
