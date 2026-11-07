from pathlib import Path
import bpy,bmesh,json
R=Path(__file__).resolve().parent;O=R/'out/photo_final_W'
bpy.ops.wm.open_mainfile(filepath=str(O/'u2_photo_scene.blend'));ob=next(o for o in bpy.context.scene.objects if o.name.startswith('SEAT-FABRIC'));ob.modifiers.clear()
bm=bmesh.new();bm.from_mesh(ob.data);print('FABRIC_BASE',len(bm.verts),len(bm.faces),'boundary',sum(e.is_boundary for e in bm.edges),'nonmanifold',sum(not e.is_manifold for e in bm.edges),flush=True)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));print('REPAIRED',len(bm.verts),len(bm.faces),'boundary',sum(e.is_boundary for e in bm.edges),flush=True);bm.to_mesh(ob.data);bm.free()
md=ob.modifiers.new('Closed upholstery remesh','REMESH');md.mode='VOXEL';md.voxel_size=.0035;md.use_smooth_shade=True
eval=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=eval.to_mesh();print('EVALUATED',len(me.vertices),flush=True)
for j in range(3):print('BOUNDS',j,min(v.co[j] for v in me.vertices),max(v.co[j] for v in me.vertices),flush=True)
