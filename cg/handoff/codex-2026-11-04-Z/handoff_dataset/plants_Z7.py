"""Z7 plants: one planter family (warm-grey matte stone, same taper/rim, graded sizes).
Window: Pachira ~2.0 m in L planter. Kitchen pair: Monstera ~1.7 m (window side, original pot removed)
in a wide M planter + smaller Pachira ~1.35 m (wall side) in an S planter."""
import bpy,bmesh,math
from mathutils import Matrix,Vector
def bbox(objs):
    ps=[o.matrix_world@Vector(c) for o in objs for c in o.bound_box];return [min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]
def lathe(name,prof,mat,col,seg=128):
    bm=bmesh.new();rings=[[bm.verts.new((r*math.cos(2*math.pi*i/seg),r*math.sin(2*math.pi*i/seg),z)) for r,z in prof] for i in range(seg)]
    for i in range(seg):
        A,B=rings[i],rings[(i+1)%seg]
        for k in range(len(prof)-1):
            try:bm.faces.new((A[k],B[k],B[k+1],A[k+1]))
            except ValueError:pass
    bmesh.ops.remove_doubles(bm,verts=bm.verts[:],dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();[setattr(p,'use_smooth',True) for p in me.polygons]
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(mat);return ob
def materials():
    m=bpy.data.materials.new('Planter_stone_warmgrey_Z7');m.use_nodes=True;nt=m.node_tree;b=nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value=.82
    nz=nt.nodes.new('ShaderNodeTexNoise');nz.inputs['Scale'].default_value=60;nz.inputs['Detail'].default_value=8
    cr=nt.nodes.new('ShaderNodeValToRGB');e=cr.color_ramp.elements;e[0].color=(.105,.098,.091,1);e[1].color=(.135,.127,.118,1)
    nt.links.new(nz.outputs['Fac'],cr.inputs['Fac']);nt.links.new(cr.outputs['Color'],b.inputs['Base Color'])
    n2=nt.nodes.new('ShaderNodeTexNoise');n2.inputs['Scale'].default_value=400;bp=nt.nodes.new('ShaderNodeBump');bp.inputs['Strength'].default_value=.10
    nt.links.new(n2.outputs['Fac'],bp.inputs['Height']);nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    s=bpy.data.materials.new('Planter_soil_Z7');s.use_nodes=True;sb=s.node_tree.nodes['Principled BSDF'];sb.inputs['Base Color'].default_value=(.035,.026,.019,1);sb.inputs['Roughness'].default_value=.95
    return m,s
def planter(tag,x,y,R,H,m,soil,col):
    rb=R*.80;rim=.012
    f=.025;rf=rb-.018
    prof=[(0,0),(rf,0),(rf+.003,.004),(rf+.003,f-.004),(rb,f),(R-.004,H-.008),(R+.002,H-.003),(R-.001,H),(R-rim,H),(R-rim-.002,H-.02),(rb-rim,f+.03),(0,f+.03)]
    lathe(f'Plant_Z7_{tag}_planter',prof,m,col).location=(x,y,0)
    lathe(f'Plant_Z7_{tag}_soil',[(0,H-.035),(R-rim-.003,H-.035)],soil,col).location=(x,y,0)
    return H-.035
def place(parts,x,y,z0,height,rot,trunk=None):
    mn,mx=bbox(parts);c=bbox([trunk])if trunk else (mn,mx);cx,cy=(c[0][0]+c[1][0])/2,(c[0][1]+c[1][1])/2
    s=height/(mx[2]-mn[2])
    for o in parts:o.matrix_world=Matrix.Translation((x,y,z0))@Matrix.Rotation(math.radians(rot),4,'Z')@Matrix.Scale(s,4)@Matrix.Translation((-cx,-cy,-mn[2]))@o.matrix_world
    return s
def pachira(tag,col):
    with bpy.data.libraries.load('/work/pach/pachira.blend',link=False) as (src,dst):dst.objects=['pachira_aquatica_01_bark_d','pachira_aquatica_01_leaves_d']
    for o in dst.objects:col.objects.link(o);o.name=f'Plant_Z7_{tag}_'+o.name.split('_')[-2]
    return dst.objects,next(o for o in dst.objects if 'bark' in o.name)
def monstera(col):
    with bpy.data.libraries.load('/work/plant2/plants_lib.blend',link=False) as (src,dst):dst.objects=['Monstera']
    o=dst.objects[0];col.objects.link(o);o.name='Plant_Z7_Monstera'
    me=o.data;bm=bmesh.new();bm.from_mesh(me)
    drop=[f for f in bm.faces if me.materials[f.material_index].name in('Ceramic','Soil')]
    bmesh.ops.delete(bm,geom=drop,context='FACES');bm.to_mesh(me);bm.free()
    return o
def apply(S):
    col=bpy.data.collections.get('Props_Z5');log={}
    for n in ['Plant_Z5_Ficus_Elastica','Plant_Z5_Peace_Lily','Plant_Z5_Monstera']:
        o=bpy.data.objects.get(n)
        if o:bpy.data.objects.remove(o,do_unlink=True)
    m,soil=materials()
    # window: Pachira L
    z=planter('PachiraL',2.73,0.95,.24,.48,m,soil,col);parts,tr=pachira('PachiraL',col);s=place(parts,2.73,0.95,z-.02,2.0-(z-.02),200,tr)
    log['window_pachira']={'planter':'D480 H480','total_h':2.0}
    # kitchen: Monstera M (window side) + Pachira S (wall side)
    z=planter('Monstera',5.00,12.20,.25,.40,m,soil,col);mo=monstera(col)
    mn,mx=bbox([mo]);place([mo],5.00,12.20,z-.01,1.70-(z-.01),15)
    log['kitchen_monstera']={'planter':'D500 H400','total_h':1.70}
    z=planter('PachiraS',5.84,12.52,.19,.32,m,soil,col);parts,tr=pachira('PachiraS',col);place(parts,5.84,12.52,z-.02,1.35-(z-.02),70,tr)
    log['kitchen_pachira']={'planter':'D380 H320','total_h':1.35}
    return log
