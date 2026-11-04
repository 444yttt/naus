import bpy,collections
for o in bpy.data.objects:
 if o.type=='MESH' and 'Linha_Warehouse' in o.name:
  print(o.name,[(m.name if m else None) for m in o.data.materials],collections.Counter(p.material_index for p in o.data.polygons),'normalz',collections.Counter(round(p.normal.z,1) for p in o.data.polygons))
for i in bpy.data.images:
 if 'MARBLE' in i.name: print('IMAGE',i.name,i.size[:],i.has_data,i.filepath)
