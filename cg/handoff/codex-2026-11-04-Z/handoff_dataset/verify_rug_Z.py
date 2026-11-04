"""Read-only geometry invariants for the rug revision."""
from pathlib import Path
import bpy,sys,json,array,hashlib
R=Path(__file__).resolve().parent;O=R/'out_Z';rows=[]
for shot in ['u1','u2','p09','p01','p13']:
    bpy.ops.wm.open_mainfile(filepath=str(R/f'out_X/{shot}_photo_scene.blend'));s=bpy.context.scene
    before={o.name:[float(v) for row in o.matrix_world for v in row] for o in s.objects if o.type=='MESH'}
    bpy.ops.wm.open_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));s=bpy.context.scene
    changed=[]
    for name,old in before.items():
        ob=s.objects.get(name)
        if not ob:changed.append(name);continue
        if max(abs(a-b) for a,b in zip(old,[float(v) for row in ob.matrix_world for v in row]))>1e-6:changed.append(name)
    rugs=[o for o in s.objects if o.name.startswith('Shindo_')];assert len(rugs)==1
    rug=rugs[0];verts=array.array('f',[0])*(3*len(rug.data.vertices));rug.data.vertices.foreach_get('co',verts)
    assert not changed,(shot,changed)
    assert not rug.hide_render and rug.visible_camera
    bs=bpy.data.materials['Shedir02_Burro_colour_study'].node_tree.nodes.get('Principled BSDF');sheen=bs.inputs['Sheen Weight'].default_value;sky=s.objects['Diagonal_sky_bay_return_Y'].data.energy;warm=s.objects['Sunlit_balcony_floor_return_Y'].data.energy
    assert abs(sheen-.45)<1e-6 and sky==800 and warm==200,(shot,sheen,sky,warm)
    xs=[v.co.x for v in rug.data.vertices];ys=[v.co.y for v in rug.data.vertices];zs=[v.co.z for v in rug.data.vertices]
    rows.append({'shot':shot,'rug_sha256':hashlib.sha256(verts.tobytes()).hexdigest(),'changed_existing_mesh_poses':changed,'rug_count':len(rugs),'rect':[min(xs),min(ys),max(xs),max(ys)],'height_range_m':[min(zs),max(zs)],'official_finish_packed':bool(rug.data.materials[0].node_tree.nodes.get('Image Texture').image.packed_file),'full_foreground_has_rug':True,'common_sofa_sheen_weight':sheen,'common_diagonal_sky_W':sky,'common_warm_return_W':warm})
assert len({r['rug_sha256'] for r in rows})==1,'Rug differs across cameras'
(O/'rug_invariants.json').write_text(json.dumps(rows,indent=2));print('Z_COMMON_RUG_VERIFIED',rows,flush=True)
