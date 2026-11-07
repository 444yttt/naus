"""Read back saved delivery scenes; verify shared layout and camera coverage."""
import bpy,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R/'out/photo_final_V';rows=[];shared_hash=None;shared_geometry=None
for shot in ['u1','u2','p09','p01','p13']:
    path=O/f'{shot}_photo_scene.blend'
    assert path.exists(),path
    bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
    bpy.context.view_layer.update()
    assert not s.render.use_border and s.render.resolution_percentage==100
    assert s.camera.name=='PhotoMatched_'+shot
    settings=json.loads((O/f'{shot}_render_settings.json').read_text(encoding='utf8'))
    assert 'sRGB' in settings['source_colour_management']
    assert not any(o.name.startswith('Shindo') for o in s.objects)
    if shot=='u1':
        near_floor=[]
        static=('LDK_floor','TV_back_wall','Kitchen_','Hall_return','Ceiling','Existing_island','Sink','Faucet','Balcony','Diagonal','TV_tile')
        for o in s.objects:
            if o.type!='MESH' or o.hide_render or o.name.startswith(static):continue
            if min((o.matrix_world@Vector(v)).z for v in o.bound_box)>.025:continue
            coords=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',coords)
            mat=np.asarray(o.matrix_world,dtype=np.float32);world=coords.reshape(-1,3)@mat[:3,:3].T+mat[:3,3]
            points=world[(world[:,2]>=-.005)&(world[:,2]<=.020),:2]
            if len(points):near_floor.append(points)
        xy=np.concatenate(near_floor) if near_floor else np.empty((0,2))
        xy=np.unique(np.round(xy/.015).astype(int),axis=0)*.015
        (O/'contact_candidates.json').write_text(json.dumps({'status':'rendered model vertices within -5 to +20mm of common floor; 15mm XY quantization, not surveyed contacts','xy_m':xy.tolist()},indent=2),encoding='utf8')
    roots=[bpy.data.objects['Beolab28_OFFICIAL_'+str(j)] for j in range(2)]
    positions=[list(o.location) for o in roots]
    assert abs(positions[0][0]-positions[1][0])<1e-5
    assert abs((positions[0][1]+positions[1][1])/2-2.35)<1e-5
    assert all(abs(abs(p[1]-2.35)-1.55)<1e-5 for p in positions)
    angles=[];heights=[]
    for root in roots:
        desired=Vector((6.30-root.location.x,2.35-root.location.y,0)).normalized()
        facing=(root.rotation_euler.to_matrix()@Vector((0,-1,0))).normalized()
        angle=math.degrees(math.atan2(desired.cross(facing).length,desired.dot(facing)));assert angle<.01;angles.append(angle)
        vv=[o.matrix_world@Vector(v) for o in root.children if o.type=='MESH' for v in o.bound_box]
        heights.append(max(v.z for v in vv)-min(v.z for v in vv))
    assert all(1.36<h<1.38 for h in heights)
    if shot=='p13':
        island=bpy.data.objects['Existing_island_plan_proxy']
        assert island.visible_camera and island.is_shadow_catcher
    geometry=[(o.name,[[round(float(v),6) for v in row] for row in o.matrix_world], [round(float(v),6) for v in o.dimensions]) for o in sorted(s.objects,key=lambda o:o.name) if o.type in ['MESH','CURVE'] and not o.name.startswith(('TV_tile_photo_recess','Balcony_reflection_photo','Diagonal_reflection_photo'))]
    digest=hashlib.sha256(json.dumps(geometry,sort_keys=True).encode()).hexdigest()
    if shared_hash is None:shared_hash=digest;shared_geometry=geometry
    if digest!=shared_hash:
        old={g[0]:g[1:] for g in shared_geometry};new={g[0]:g[1:] for g in geometry}
        changed=[name for name in sorted(set(old)|set(new)) if old.get(name)!=new.get(name)]
        raise AssertionError((shot,'shared geometry changed',changed))
    rows.append({'shot':shot,'native_resolution':[s.render.resolution_x,s.render.resolution_y],'border':s.render.use_border,'speaker_positions_m':positions,'speaker_height_m':heights,'speaker_aim_error_deg':angles,'rug':False,'camera':s.camera.name,'samples':s.cycles.samples,'shared_geometry_transform_sha256':digest,'source_colour_management':settings['source_colour_management']})
(O/'scene_delivery_QA.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
print('DELIVERY_SCENES_VERIFIED',len(rows))
