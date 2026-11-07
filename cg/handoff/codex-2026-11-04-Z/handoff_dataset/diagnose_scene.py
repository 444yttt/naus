import bpy
s=bpy.context.scene
print('SET',s.render.engine,s.view_settings.exposure,s.view_settings.view_transform,s.view_settings.look)
for ob in bpy.data.objects:
 if ob.type=='LIGHT': print('LIGHT',ob.name,ob.data.energy)
for m in bpy.data.materials:
 if m.name.startswith('Torii_grey'):
  for n in m.node_tree.nodes:
   if n.type=='BSDF_PRINCIPLED': print([(i.name,i.default_value[: ] if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if hasattr(i,'default_value')])
print('OVERRIDE',s.view_layers[0].material_override)
