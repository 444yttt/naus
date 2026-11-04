import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent; W=R/'out/photo_final_W'; O=R/'out_X';O.mkdir(exist_ok=True)
files=[W/'Harajuku_3LDK_delivery_W.zip',W/'delivery/source/Harajuku_LDK_W.blend']
(O/'input_sha256.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
out={}
for shot in ['u1','u2','p09','p01','p13']:
 bpy.ops.wm.open_mainfile(filepath=str(W/f'{shot}_photo_scene.blend'));s=bpy.context.scene
 objects={}
 for ob in s.objects:
  if ob.type in ['MESH','EMPTY','LIGHT','CAMERA']:
   row={'type':ob.type,'matrix_world':[list(r) for r in ob.matrix_world],'location':list(ob.location),'rotation':list(ob.rotation_euler),'dimensions':list(ob.dimensions)}
   if ob.type=='MESH':
    bb=[ob.matrix_world@Vector(v) for v in ob.bound_box];row.update(min=[min(v[i] for v in bb) for i in range(3)],max=[max(v[i] for v in bb) for i in range(3)],materials=[m.name if m else None for m in ob.data.materials])
   if ob.type=='LIGHT':row.update(energy=ob.data.energy,color=list(ob.data.color),light_type=ob.data.type)
   if ob.type=='CAMERA':row.update(lens=ob.data.lens,shift_x=ob.data.shift_x,shift_y=ob.data.shift_y)
   objects[ob.name]=row
 mats={}
 for m in bpy.data.materials:
  if m.use_nodes:
   mats[m.name]=[{'type':n.type,'name':n.name,'inputs':{i.name:list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value for i in n.inputs if hasattr(i,'default_value') and isinstance(i.default_value,(float,int)) or hasattr(i,'default_value') and hasattr(i.default_value,'__len__')}} for n in m.node_tree.nodes if n.type in ['BSDF_PRINCIPLED','BACKGROUND']]
 out[shot]={'camera':s.camera.name,'objects':objects,'materials':mats}
(O/'before_snapshot.json').write_text(json.dumps(out,indent=2))
print('SNAPSHOT_DONE')
