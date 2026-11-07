import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
S=bpy.context.scene;cam=S.camera;dg=bpy.context.evaluated_depsgraph_get()
W,H=S.render.resolution_x,S.render.resolution_y
fr=[cam.matrix_world@v for v in cam.data.view_frame(scene=S)]  # tr,br,bl,tl
tr,br,bl,tl=fr;o=cam.matrix_world.translation
def ray(px,py):
    u=(px+.5)/W;v=(py+.5)/H
    top=tl+(tr-tl)*u;bot=bl+(br-bl)*u;p=top+(bot-top)*v
    d=(p-o).normalized();return d
def tree(name):
    ob=bpy.data.objects[name];b=bmesh.new();b.from_object(ob,dg);b.transform(ob.matrix_world);bmesh.ops.triangulate(b,faces=b.faces[:]);return BVHTree.FromBMesh(b),b
tf,bf=tree('SEAT-FABRIC (C-Group#4)');ts,bs=tree('SEAT-OUTER_SHELL_BOTTOM (C-Group#6)')
pts=json.load(open('/work/trial/red_px.json'));res=[]
for px,py in pts:
    d=ray(px,py);hf=tf.ray_cast(o,d);hs=ts.ray_cast(o,d)
    res.append({'px':[px,py],'fab_dist':hf[3],'shell_dist':hs[3],'fab_pt':list(hf[0]) if hf[0] else None,'fab_n':list(hf[1]) if hf[1] else None,'face':hf[2]})
ok=[r for r in res if r['fab_dist'] is not None]
import statistics
diff=[ (r['shell_dist']-r['fab_dist']) if r['shell_dist'] else None for r in ok]
print('RAY n',len(res),'fabhit',len(ok),'shellhit',sum(1 for r in ok if r['shell_dist']))
dd=[x for x in diff if x is not None];print('shell-minus-fab mm min/med/max',min(dd)*1000,statistics.median(dd)*1000,max(dd)*1000)
zs=[r['fab_pt'][2] for r in ok];print('fab z range',min(zs),max(zs))
faces=sorted(set(r['face'] for r in ok));print('faces',len(faces))
# distance from the hit fabric points to the shell surface (nearest)
nd=[ts.find_nearest(Vector(r['fab_pt']))[3]*1000 for r in ok];print('nearest shell mm min/med/max',min(nd),statistics.median(nd),max(nd))
json.dump(res,open('/work/trial/ray_res.json','w'))
streak=[r for r in ok if r['shell_dist']]
print('STREAK n',len(streak))
bf.faces.ensure_lookup_table()
import math
for r in streak[:200:10]:
    f=bf.faces[r['face']];L=[e.calc_length() for e in f.edges];A=f.calc_area()
    print('F',r['face'],'edges_mm',[round(x*1000,1) for x in L],'area_mm2',round(A*1e6,2),'z',round(r['fab_pt'][2],3),'n',[round(x,2) for x in r['fab_n']],'infront_mm',round((r['shell_dist']-r['fab_dist'])*1000,1))
