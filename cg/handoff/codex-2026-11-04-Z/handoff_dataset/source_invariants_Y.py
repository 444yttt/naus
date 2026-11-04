from pathlib import Path
import bpy,json,hashlib,array
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R/'out_Y';rows=[]
static=('LDK_floor','TV_back_wall','Kitchen_wall','Hall_return','Kitchen_top_wall','Ceiling','Kitchen_cabinet','Kitchen_wall_counter','Existing_island','Sink','Faucet','Balcony_overhang','Balcony_reflection_photo','Diagonal_reflection_photo','TV_tile_')
def pose(ob):return [float(v) for row in ob.matrix_world for v in row]
def lights(S):return {ob.name:{'matrix':pose(ob),'energy':float(ob.data.energy),'colour':list(ob.data.color),'shape':ob.data.shape if ob.data.type=='AREA' else None,'size':float(ob.data.size) if ob.data.type=='AREA' else None,'glossy':ob.visible_glossy,'specular':float(ob.data.specular_factor)} for ob in S.objects if ob.type=='LIGHT'}
for shot in ['u1','u2','p09','p01','p13']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'out_X/{shot}_photo_scene.blend'));S=bpy.context.scene;old={o.name:pose(o) for o in S.objects if o.type in ['MESH','CURVE']};lc=lights(S);oldcam=pose(S.camera);world={i.name: list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value for i in S.world.node_tree.nodes['Background'].inputs if i.name in ['Color','Strength']}
 bpy.ops.wm.open_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));S=bpy.context.scene;newlights=lights(S);changes={k:max(abs(a-b) for a,b in zip(p,pose(S.objects[k]))) for k,p in old.items() if k in S.objects and max(abs(a-b) for a,b in zip(p,pose(S.objects[k])))>1e-7}
 layout=[(o.name,[round(v,6) for v in pose(o)]) for o in sorted(S.objects,key=lambda x:x.name) if o.type in ['MESH','CURVE'] and not o.name.startswith(static)]
 cloth=next(o for o in S.objects if o.name.startswith('SEAT-FABRIC'));co=array.array('f',[0])*(len(cloth.data.vertices)*3);cloth.data.vertices.foreach_get('co',co)
 feet=[]
 for ob in S.objects:
  if ob.type=='MESH' and ob.name.startswith(('SEAT-GLIDE','C-TORII_SMAL','IVRESSE_black_chrome_base')):feet.append({'object':ob.name,'min_world_z_m':min((ob.matrix_world@v.co).z for v in ob.data.vertices)})
 row={'shot':shot,'mesh_pose_changes_vs_X':changes,'original_light_changes':{k:{'X':v,'Y':newlights.get(k)} for k,v in lc.items() if newlights.get(k)!=v},'new_lights':{k:v for k,v in newlights.items() if k not in lc},'world_unchanged':all((list(S.world.node_tree.nodes['Background'].inputs[k].default_value) if isinstance(v,list) else S.world.node_tree.nodes['Background'].inputs[k].default_value)==v for k,v in world.items()),'camera_matrix_delta_vs_X':max(abs(a-b) for a,b in zip(oldcam,pose(S.camera))),'common_furniture_pose_sha256':hashlib.sha256(json.dumps(layout).encode()).hexdigest(),'Eames_cushion_sha256':hashlib.sha256(co.tobytes()).hexdigest(),'foot_geometry':feet,'rug_present':any(o.name.startswith('Shindo') for o in S.objects)}
 rows.append(row);assert not changes and not row['original_light_changes'] and row['world_unchanged'] and not row['rug_present'];assert shot in ['u2','p13'] or row['camera_matrix_delta_vs_X']==0
assert len({r['common_furniture_pose_sha256'] for r in rows})==1
assert len({r['Eames_cushion_sha256'] for r in rows})==1
(O/'source_invariants_Y.json').write_text(json.dumps(rows,indent=2));print('Y_SOURCE_INVARIANTS_VERIFIED',[(r['shot'],len(r['new_lights'])) for r in rows],flush=True)
