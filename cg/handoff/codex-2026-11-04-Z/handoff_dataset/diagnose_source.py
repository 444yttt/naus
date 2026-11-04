import bpy,collections
for o in bpy.data.objects:
 if o.type=='MESH' and o.name=='ERNEST_sofa_80':
  print('TRANSFORMS',o.location[:],o.rotation_euler[:],o.scale[:])
  print('POLYGONS',collections.Counter(p.material_index for p in o.data.polygons))
  print('SLOTS',[(s.link,s.material.name) for s in o.material_slots])
