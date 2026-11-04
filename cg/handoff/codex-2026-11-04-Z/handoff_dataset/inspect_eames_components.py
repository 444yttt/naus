import bpy
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=str(Path('handoff_dataset/models/eames_official/source.blend').resolve()))
for ob in bpy.data.objects:
 if ob.type!='MESH' or not any(x in ob.name for x in ['FABRIC','BASE','SHELL']):continue
 adj=[[] for v in ob.data.vertices]
 for e in ob.data.edges:a,b=e.vertices;adj[a].append(b);adj[b].append(a)
 seen=set();out=[]
 for k in range(len(adj)):
  if k in seen:continue
  q=[k];seen.add(k);comp=[]
  while q:
   j=q.pop();comp.append(j)
   for v in adj[j]:
    if v not in seen:seen.add(v);q.append(v)
  if len(comp)>20:
   ps=[ob.matrix_world@ob.data.vertices[i].co for i in comp]
   out.append((len(comp),[(round(min(p[i] for p in ps),3),round(max(p[i] for p in ps),3)) for i in range(3)]))
 print(ob.name,out)
