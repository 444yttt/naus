# Eames rear-opening sliver fix (Z2), view-independent and deterministic.
# W's repaired SEAT-FABRIC keeps thin underside slivers inside the seat shell bowl. The
# rear of SEAT-OUTER_SHELL_BOTTOM is open (rear skin omitted in W), so at native size
# those slivers show as white/gold streaks against the dark shell interior (u2).
# Deleted: fabric faces whose vertices are all below z=0.32, inside the bowl (shell hit
# along +Y, -Y and -Z within 0.08 m) and within 25 mm of the shell surface. These are the
# cushion underside, covered by the shell from every direction except that opening.
import bpy,bmesh,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def fix(S=None,apply=True):
    fab=bpy.data.objects['SEAT-FABRIC (C-Group#4)'];sh=bpy.data.objects['SEAT-OUTER_SHELL_BOTTOM (C-Group#6)']
    dg=bpy.context.evaluated_depsgraph_get()
    b=bmesh.new();b.from_object(sh,dg);b.transform(sh.matrix_world);bmesh.ops.triangulate(b,faces=b.faces[:]);T=BVHTree.FromBMesh(b);b.free()
    mw=fab.matrix_world;bm=bmesh.new();bm.from_mesh(fab.data);bm.verts.ensure_lookup_table()
    under=set()
    for v in bm.verts:
        w=mw@v.co
        if w.z>=0.32:continue
        if T.find_nearest(w)[3]>0.025:continue
        if T.ray_cast(w,Vector((0,1,0)),.8)[0] is None or T.ray_cast(w,Vector((0,-1,0)),.8)[0] is None:continue
        hz=T.ray_cast(w,Vector((0,0,-1)),.08)[0]
        if hz is None:continue
        under.add(v.index)
    faces=[f for f in bm.faces if all(v.index in under for v in f.verts)]
    info={'underside_vertices':len(under),'deleted_faces':len(faces),'fabric_faces_before':len(bm.faces)}
    if apply and faces:
        bmesh.ops.delete(bm,geom=faces,context='FACES_ONLY');bm.to_mesh(fab.data);fab.data.update()
    info['fabric_faces_after']=len(fab.data.polygons)
    info['fabric_sha256']=hashlib.sha256(repr([tuple(round(c,7) for c in v.co) for v in fab.data.vertices]+[tuple(p.vertices) for p in fab.data.polygons]).encode()).hexdigest()
    bm.free();return info
