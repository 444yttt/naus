import bpy
from mathutils import Vector
for o in bpy.data.objects:
 if 'Ernest_DEALER' in o.name:
  v=[o.matrix_world@Vector(p) for p in o.bound_box]
  print(o.name,'hide',o.hide_render,'parent',o.parent,'bounds',[(min(x[i] for x in v),max(x[i] for x in v)) for i in range(3)],'scale',o.scale[:])
