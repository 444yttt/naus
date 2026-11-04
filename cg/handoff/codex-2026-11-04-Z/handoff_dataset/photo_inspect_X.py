"""Read-only scene checks and original-pixel detail sheets for the W revision."""
from pathlib import Path
import bpy,sys,json,math,hashlib,array
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parent;O=R/'out_X';rows=[]
for shot in ['u1','u2','p09','p01','p13']:
 bpy.ops.wm.open_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));S=bpy.context.scene
 W,H=S.render.resolution_x,S.render.resolution_y;deps=bpy.context.evaluated_depsgraph_get()
 contacts=[];seen=set()
 for ob in S.objects:
  if ob.type!='MESH' or ob.hide_render or not ob.visible_camera:continue
  if not (ob.name.startswith(('SEAT-GLIDE','IVRESSE_black_chrome_base','C-TORII_SMAL','Linha_Warehouse','Ernest_DEALER','beolab-28_woofer','Rear_table_support'))):continue
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co
   if not -.001<=p.z<=.006:continue
   key=tuple(round(t/.015) for t in p)
   if key in seen:continue
   seen.add(key);uv=world_to_camera_view(S,S.camera,p)
   if uv.z<=0 or not 0<uv.x<1 or not 0<uv.y<1:continue
   direction=p-S.camera.location;dist=direction.length
   hit,loc,normal,index,hitob,matrix=S.ray_cast(deps,S.camera.location,direction.normalized(),distance=dist+.02)
   if not hit or abs((loc-S.camera.location).length-dist)>.025:continue
   contacts.append({'object':ob.name,'world_m':list(p),'pixel':[uv.x*W,(1-uv.y)*H]})
 roots=[list(bpy.data.objects['Beolab28_OFFICIAL_'+str(j)].location) for j in range(2)]
 assert abs(abs(roots[0][1]-2.35)-abs(roots[1][1]-2.35))<1e-5
 assert abs(roots[0][0]-roots[1][0])<1e-6
 static=('LDK_floor','TV_back_wall','Kitchen_wall','Hall_return','Kitchen_top_wall','Ceiling','Kitchen_cabinet','Kitchen_wall_counter','Existing_island','Sink','Faucet','Balcony_overhang','Balcony_reflection_photo','Diagonal_reflection_photo','TV_tile_')
 layout=[(o.name,[round(float(v),5) for row in o.matrix_world for v in row],[round(float(v),5) for v in o.dimensions]) for o in sorted(S.objects,key=lambda o:o.name) if o.type in ['MESH','CURVE'] and not o.name.startswith(static)]
 signature=hashlib.sha256(json.dumps(layout).encode()).hexdigest()
 cloth=next(o for o in S.objects if o.name.startswith('SEAT-FABRIC'));co=array.array('f',[0])*(3*len(cloth.data.vertices));cloth.data.vertices.foreach_get('co',co)
 geometry_signature=hashlib.sha256(co.tobytes()).hexdigest()
 rows.append({'shot':shot,'native_size':[W,H],'furniture_layout_sha256':signature,'eames_cushion_geometry_sha256':geometry_signature,'visible_floor_contact_candidates':contacts,'speaker_roots':roots,'camera_location':list(S.camera.location),'no_rug':not any(o.name.startswith('Shindo') for o in S.objects),'eames_shell_subdivision':[m.render_levels for o in S.objects if o.name.startswith('SEAT-OUTER_SHELL') for m in o.modifiers if m.type=='SUBSURF']})
assert len({r['furniture_layout_sha256'] for r in rows})==1,'Per-view furniture layout differs'
assert len({r['eames_cushion_geometry_sha256'] for r in rows})==1,'Per-view cushion geometry differs'
(O/'scene_inspection.json').write_text(json.dumps(rows,indent=2))
print('W_SCENES_CHECKED',[(r['shot'],len(r['visible_floor_contact_candidates'])) for r in rows],flush=True)
