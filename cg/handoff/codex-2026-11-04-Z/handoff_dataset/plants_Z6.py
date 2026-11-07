"""Z6: tall plants (user: 1.7-2 m class). Ficus elastica -> ~1.85 m, Monstera -> ~1.75 m (user-supplied
pack, rescaled about the pot base), Peace Lily replaced by Poly Haven 'Pachira Aquatica 01' variant d
(CC0) in a matte stone planter, total ~2.0 m."""
import bpy,bmesh,math
from mathutils import Matrix,Vector
def bbox(o):
    ps=[o.matrix_world@Vector(c) for c in o.bound_box];return [min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]
def rescale_to(o,h,xy):
    mn,mx=bbox(o);s=h/(mx[2]-mn[2]);cx,cy=(mn[0]+mx[0])/2,(mn[1]+mx[1])/2
    o.matrix_world=Matrix.Translation((xy[0],xy[1],0))@Matrix.Scale(s,4)@Matrix.Translation((-cx,-cy,-mn[2]))@o.matrix_world
    return s
def lathe(name,prof,mat,col,seg=96):
    bm=bmesh.new();rings=[[bm.verts.new((r*math.cos(2*math.pi*i/seg),r*math.sin(2*math.pi*i/seg),z)) for r,z in prof] for i in range(seg)]
    for i in range(seg):
        A,B=rings[i],rings[(i+1)%seg]
        for k in range(len(prof)-1):
            try:bm.faces.new((A[k],B[k],B[k+1],A[k+1]))
            except ValueError:pass
    bmesh.ops.remove_doubles(bm,verts=bm.verts[:],dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();[setattr(p,'use_smooth',True) for p in me.polygons]
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(mat);return ob
def pachira(tag,x,y,rot,col,m,soil,H=.42):
    pass
    pot=lathe(f'Plant_Z6_{tag}_planter',[(0,0),(.20,0),(.205,.01),(.23,.20),(.235,H-.01),(.232,H),(.21,H),(.205,H-.04),(0,H-.04)],m,col)
    pot.location=(x,y,0)
    disc=lathe(f'Plant_Z6_{tag}_soil',[(0,H-.045),(.206,H-.045)],soil,col);disc.location=(x,y,0)
    with bpy.data.libraries.load('/work/pach/pachira.blend',link=False) as (src,dst):dst.objects=['pachira_aquatica_01_bark_d','pachira_aquatica_01_leaves_d']
    parts=[o for o in dst.objects]
    for o in parts:col.objects.link(o);o.name=f'Plant_Z6_{tag}_'+o.name.split('_')[-2]
    mn=[min(bbox(o)[0][i] for o in parts) for i in range(3)];mx=[max(bbox(o)[1][i] for o in parts) for i in range(3)]
    bark=next(o for o in parts if 'bark' in o.name);bmn,bmx=bbox(bark);cx,cy=(bmn[0]+bmx[0])/2,(bmn[1]+bmx[1])/2
    s=(2.0-H+.04)/(mx[2]-mn[2])
    for o in parts:o.matrix_world=Matrix.Translation((x,y,H-.06))@Matrix.Rotation(math.radians(rot),4,'Z')@Matrix.Scale(s,4)@Matrix.Translation((-cx,-cy,-mn[2]))@o.matrix_world
    return {'xy':[x,y],'scale':s,'total_h':round(H-.06+s*(mx[2]-mn[2]),3)}
def apply(S):
    col=bpy.data.collections.get('Props_Z5');log={}
    fi=bpy.data.objects.get('Plant_Z5_Ficus_Elastica')
    if fi:bpy.data.objects.remove(fi,do_unlink=True)
    ob=bpy.data.objects.get('Plant_Z5_Monstera');log['monstera_scale']=rescale_to(ob,1.75,(5.02,12.22))
    pl=bpy.data.objects.get('Plant_Z5_Peace_Lily')
    if pl:bpy.data.objects.remove(pl,do_unlink=True)
    m=bpy.data.materials.new('Planter_stone_matte_Z6');m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.10,.095,.09,1);b.inputs['Roughness'].default_value=.72
    nz=m.node_tree.nodes.new('ShaderNodeTexNoise');nz.inputs['Scale'].default_value=180;bp=m.node_tree.nodes.new('ShaderNodeBump');bp.inputs['Strength'].default_value=.12;m.node_tree.links.new(nz.outputs['Fac'],bp.inputs['Height']);m.node_tree.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    soil=bpy.data.materials.new('Planter_soil_Z6');soil.use_nodes=True;sb=soil.node_tree.nodes['Principled BSDF'];sb.inputs['Base Color'].default_value=(.03,.022,.016,1);sb.inputs['Roughness'].default_value=.95
    log['pachira_kitchen']=pachira('Pachira_kitchen',5.86,12.55,35,col,m,soil)
    log['pachira_window']=pachira('Pachira_window',2.73,0.95,200,col,m,soil)
    return log
