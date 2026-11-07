"""Extract model floor-contact components for projection diagnostics."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_S'
bpy.ops.wm.open_mainfile(filepath=str(O/'u1_photo_scene.blend'));bpy.context.view_layer.update()
static=('LDK_floor','TV_back_wall','Kitchen_wall','Hall_return','Kitchen_top_wall','Ceiling','Kitchen_cabinet','Kitchen_wall_counter','Existing_island','Sink','Faucet','Balcony_overhang','Balcony_reflection_photo','Diagonal_reflection_photo','Shindo','TV_tile')
points=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or ob.name.startswith(static):continue
 co={v.index:ob.matrix_world@v.co for v in ob.data.vertices}
 near={i for i,v in co.items() if -.004<=v.z<=.012}
 if not near:continue
 edges={i:[] for i in near}
 for e in ob.data.edges:
  a,b=e.vertices
  if a in near and b in near:edges[a].append(b);edges[b].append(a)
 while near:
  start=near.pop();stack=[start];comp=[start]
  while stack:
   for k in edges[stack.pop()]:
    if k in near:near.remove(k);stack.append(k);comp.append(k)
  center=sum((co[i] for i in comp),Vector())/len(comp)
  root=ob
  while root.parent:root=root.parent
  if not any(p['group']==root.name and (Vector(p['point'])-center).length<.06 for p in points):points.append({'group':root.name,'mesh':ob.name,'point':list(center),'floor_z_m':center.z})
(O/'model_floor_contacts.json').write_text(json.dumps({'method':'connected source-mesh vertex components within[-4,+12]mm of common z=0 floor; diagnostic only, not measured room contact observations','contacts':points},indent=2),encoding='utf8');print('MODEL_CONTACTS',len(points))
