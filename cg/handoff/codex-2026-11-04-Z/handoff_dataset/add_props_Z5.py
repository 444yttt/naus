"""Z5 common-scene changes (user 2026-11-04): plants at the marked plan positions (user-supplied
indoor-plants model), Beosound Balance removed, Ernest finish with a less brown base (same dark grain),
silver flatware stand-ins for the requested Hermes set at the six seats, three Panthella-type portable
lamps on the dining table, and objects on the coffee tables. Applied identically in every view."""
import bpy,bmesh,math
from mathutils import Vector,Matrix
PLANTS='/work/plant2/plants_lib.blend'
def mat(name,col,rough=.5,metal=0,coat=0,sheen=0):
    m=bpy.data.materials.get(name)
    if m:return m
    m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=col+(1,);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;b.inputs['Coat Weight'].default_value=coat
    if sheen:b.inputs['Sheen Weight'].default_value=sheen
    return m
def link(ob,S,col):
    col.objects.link(ob);return ob
def outline_obj(name,pts,thick,m,S,col,bevel=.0012):
    bm=bmesh.new();vs=[bm.verts.new((x,y,0)) for x,y in pts];f=bm.faces.new(vs)
    r=bmesh.ops.extrude_face_region(bm,geom=[f]);bmesh.ops.translate(bm,verts=[v for v in r['geom'] if isinstance(v,bmesh.types.BMVert)],vec=(0,0,thick))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);link(ob,S,col);me.materials.append(m)
    bv=ob.modifiers.new('bevel','BEVEL');bv.width=bevel;bv.segments=3;bv.limit_method='ANGLE'
    ob.modifiers.new('ws','WEIGHTED_NORMAL');[setattr(p,'use_smooth',True) for p in me.polygons]
    return ob
def lathe(name,prof,m,S,col,seg=48):
    bm=bmesh.new();rings=[]
    for i in range(seg):
        a=2*math.pi*i/seg;rings.append([bm.verts.new((r*math.cos(a),r*math.sin(a),z)) for r,z in prof])
    for i in range(seg):
        A=rings[i];B=rings[(i+1)%seg]
        for k in range(len(prof)-1):
            try:bm.faces.new((A[k],B[k],B[k+1],A[k+1]))
            except ValueError:pass
    bmesh.ops.remove_doubles(bm,verts=bm.verts[:],dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();[setattr(p,'use_smooth',True) for p in me.polygons]
    ob=bpy.data.objects.new(name,me);link(ob,S,col);me.materials.append(m);return ob
def hermes_plate_material():
    m=bpy.data.materials.get('Plate_porcelain_platinum_mosaic_Z5')
    if m:return m
    m=bpy.data.materials.new('Plate_porcelain_platinum_mosaic_Z5');m.use_nodes=True;nt=m.node_tree;nn=nt.nodes;ll=nt.links
    out=nn['Material Output'];por=nn['Principled BSDF']
    por.inputs['Base Color'].default_value=(.86,.855,.84,1);por.inputs['Roughness'].default_value=.18;por.inputs['Coat Weight'].default_value=.7;por.inputs['Coat Roughness'].default_value=.05
    pt=nn.new('ShaderNodeBsdfPrincipled');pt.inputs['Base Color'].default_value=(.60,.61,.63,1);pt.inputs['Metallic'].default_value=1;pt.inputs['Roughness'].default_value=.12
    tc=nn.new('ShaderNodeTexCoord');sp=nn.new('ShaderNodeSeparateXYZ');ll.new(tc.outputs['Object'],sp.inputs[0])
    def M(op,a,b=None,v=None):
        n=nn.new('ShaderNodeMath');n.operation=op
        for i,x in enumerate([a,b]):
            if x is None:continue
            if isinstance(x,(int,float)):n.inputs[i].default_value=x
            else:ll.new(x,n.inputs[i])
        return n.outputs[0]
    r=M('SQRT',M('ADD',M('MULTIPLY',sp.outputs[0],sp.outputs[0]),M('MULTIPLY',sp.outputs[1],sp.outputs[1])))
    ang=M('ARCTAN2',sp.outputs[1],sp.outputs[0]);arc=M('MULTIPLY',ang,.121)
    rr=M('DIVIDE',r,1.0)
    cb=nn.new('ShaderNodeCombineXYZ');ll.new(arc,cb.inputs[0]);ll.new(r,cb.inputs[1])
    br=nn.new('ShaderNodeTexBrick');br.inputs['Scale'].default_value=1;br.inputs['Mortar Size'].default_value=.00045;br.inputs['Brick Width'].default_value=.0042;br.inputs['Row Height'].default_value=.0038;br.offset=.5
    ll.new(cb.outputs[0],br.inputs['Vector'])
    # band: dinner 0.112-0.130 m, dessert (scaled by object radius ratio via Z>0.0072? use r ranges of both)
    bd=M('MULTIPLY',M('GREATER_THAN',r,.112),M('LESS_THAN',r,.130))
    bs=M('MULTIPLY',M('MULTIPLY',M('GREATER_THAN',r,.086),M('LESS_THAN',r,.101)),M('GREATER_THAN',sp.outputs[2],.0095))
    band=M('MAXIMUM',M('MULTIPLY',bd,M('LESS_THAN',M('ADD',sp.outputs[2],0),.03)),bs)
    tiles=M('MULTIPLY',band,M('SUBTRACT',1.0,br.outputs['Fac']))
    mix=nn.new('ShaderNodeMixShader');ll.new(tiles,mix.inputs[0]);ll.new(por.outputs[0],mix.inputs[1]);ll.new(pt.outputs[0],mix.inputs[2]);ll.new(mix.outputs[0],out.inputs['Surface'])
    return m
def place(ob,loc,yaw,z=0):ob.matrix_world=Matrix.Translation(Vector((loc[0],loc[1],z)))@Matrix.Rotation(yaw,4,'Z')@ob.matrix_world
def ellipse(cx,cy,rx,ry,n=24,a0=0,a1=2*math.pi):return [(cx+rx*math.cos(a0+(a1-a0)*i/n),cy+ry*math.sin(a0+(a1-a0)*i/n)) for i in range(n+1)]
def apply(S):
    col=bpy.data.collections.new('Props_Z5');S.collection.children.link(col);log={}
    # 1 remove Beosound Balance
    rm=[o.name for o in list(S.objects) if 'alance' in o.name or 'eosound' in o.name.lower()]
    for n in rm:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
    log['removed']=rm
    # 2 coffee-table finish: same grain recipe, base without the brown cast
    import ernest_wood_Z2 as ew,ernest_wood_Z4 as e4
    old=bpy.data.materials['Ernest_dark_wood_grain_Z4'];ew.P.update(e4.P);ew.BASE=(0.0108,0.0099,0.0093);m5=ew.build();m5.name='Ernest_dark_wood_grain_Z5';n=0
    for name in ew.TARGETS:
        for s in bpy.data.objects[name].material_slots:
            if s.material==old:s.material=m5;n+=1
    log['wood']={'slots':n,'base_rgb':ew.BASE,'params':e4.P}
    # 3 plants
    with bpy.data.libraries.load(PLANTS,link=False) as (src,dst):dst.objects=[x for x in src.objects if x in('Monstera','Peace Lily','Ficus Elastica')]
    spec={'Monstera':((5.08,12.38),1.25,.6),'Peace Lily':((5.83,12.64),1.0,2.1),'Ficus Elastica':((2.73,0.68),1.35,4.0)}
    for ob in dst.objects:
        (x,y),s,yaw=spec[ob.name];ob.name='Plant_Z5_'+ob.name.replace(' ','_');col.objects.link(ob)
        ob.matrix_world=Matrix.Translation((x,y,0))@Matrix.Rotation(yaw,4,'Z')@Matrix.Scale(s,4)
    log['plants']={k:{'xy':v[0],'scale':v[1]} for k,v in spec.items()}
    # 4 dining: Hermes H Deco plates (user-supplied CGMood model) + user-supplied classic cutlery set, leather placemats
    with bpy.data.libraries.load('/work/herm/tableware_lib.blend',link=False) as (src,dst2):dst2.objects=list(src.objects)
    LIB={o.name:o for o in dst2.objects}
    import tableware_Z5 as _tw;silver=_tw.silver()
    c=Vector((3.91,5.5));a=math.radians(71.1);u=Vector((math.cos(a),math.sin(a)));nv=Vector((-u.y,u.x));top=0.74
    knife=[(-.120,-.0075),(-.010,-.0085),(.0,-.0065),(.12,-.0055),(.125,0),(.12,.0080),(.0,.0085),(-.010,.0090),(-.120,.0075),(-.125,0)]
    fork=[(-.105,-.0075),(.020,-.0050),(.040,-.0110),(.100,-.0120),(.100,-.0085),(.050,-.0070),(.050,-.0030),(.100,-.0035),(.100,.0005),(.050,.0002),(.050,.0040),(.100,.0040),(.100,.0080),(.050,.0076),(.050,.0110),(.100,.0115),(.100,.0125),(.040,.0120),(.020,.0050),(-.105,.0075),(-.110,0)]
    spoon_h=[(-.105,-.0072),(.030,-.0035),(.045,-.0040),(.045,.0040),(.030,.0035),(-.105,.0072),(-.110,0)]
    k=0
    for r in [o for o in S.objects if o.name.startswith('Torii_USER_MODEL_')]:
        p=Vector(r.matrix_world.translation[:2]);rel=p-c;along=rel.dot(u);side=1 if rel.dot(nv)>0 else -1
        setting=c+u*along+nv*side*(0.575-0.29);face=-nv*side           # diner faces toward table centre line
        yaw=math.atan2(face.y,face.x);left=Vector((-face.y,face.x))
        import tableware_Z5 as tw
        mt=tw.placemat(f'Placemat_Z5_{k}',col);mt.matrix_world=Matrix.Translation((setting.x,setting.y,top))@Matrix.Rotation(yaw+math.pi/2,4,'Z')
        z=top+0.003
        def put(libname,newname,loc,ang,zz):
            src=LIB[libname];ob=src.copy();ob.name=newname;col.objects.link(ob)
            ob.matrix_world=Matrix.Translation((loc.x,loc.y,zz))@Matrix.Rotation(ang,4,'Z');return ob
        put('HDeco_presentation_plate_black_D31',f'Plate_Z5_{k}_presentation',setting,yaw,z)
        put('HDeco_dinner_plate_white_D26',f'Plate_Z5_{k}_dinner',setting,yaw,z+0.0023)
        tip=yaw+math.pi          # library pieces point their tip along local -X; tip faces the table centre
        put('Cutlery_dinner_fork',f'Flatware_Z5_{k}_fork',setting+left*0.188,tip,z)
        put('Cutlery_dinner_knife',f'Flatware_Z5_{k}_knife',setting-left*0.188,tip,z)
        put('Cutlery_dinner_spoon',f'Flatware_Z5_{k}_spoon',setting-left*0.222,tip,z)
        put('Cutlery_teaspoon',f'Flatware_Z5_{k}_teaspoon',setting+face*0.150,math.atan2(-left.y,-left.x)+math.pi,z)
        k+=1
    log['flatware_settings']=k
    # 5 dining lamps: Panthella-160-Portable-type (dimension based, not manufacturer CAD)
    lw=mat('Lamp_opal_white_Z5',(0.92,0.92,0.90),rough=.22,coat=.4);lb=mat('Lamp_white_body_Z5',(0.88,0.88,0.86),rough=.35)
    for i,t in enumerate([-0.78,0.0,0.78]):
        q=c+u*t
        body=lathe(f'Dining_lamp_Z5_{i}_body',[(0,0),(.055,0),(.055,.004),(.040,.010),(.018,.035),(.010,.080),(.008,.150),(.010,.185),(0,.185)],lb,S,col)
        shade=lathe(f'Dining_lamp_Z5_{i}_shade',[(0,.255)]+[(.080*math.sin(math.radians(d)),.185+.070*math.cos(math.radians(d))) for d in range(10,91,8)]+[(.080,.185),(.074,.186)],lw,S,col)
        for ob in(body,shade):ob.matrix_world=Matrix.Translation((q.x,q.y,top))
    log['lamps']=3
    # 6 coffee tables: books, sphere, bowl, small vase
    paper=[mat('Book_linen_Z5',(.62,.58,.52),.8,sheen=.2),mat('Book_charcoal_Z5',(.05,.05,.05),.7),mat('Book_sage_Z5',(.22,.26,.22),.75)]
    pages=mat('Book_pages_Z5',(.78,.76,.70),.9)
    z=.30;base=Vector((7.50,3.02));yaw=math.radians(-18)
    for i,(w,d,h,m) in enumerate([(.33,.25,.034,paper[0]),(.30,.235,.028,paper[1]),(.27,.21,.040,paper[2])]):
        bpy.ops.mesh.primitive_cube_add(size=1);ob=bpy.context.active_object;S.collection.objects.unlink(ob) if ob.name in S.collection.objects else None
        for cl in list(ob.users_collection):cl.objects.unlink(ob)
        col.objects.link(ob);ob.name=f'Coffee_book_Z5_{i}';ob.data.materials.append(m);ob.data.materials.append(pages)
        ob.scale=(w,d,h);bv=ob.modifiers.new('b','BEVEL');bv.width=.002;bv.segments=2
        ob.matrix_world=Matrix.Translation((base.x+.008*i,base.y-.006*i,z+h/2+sum([.034,.028,.040][:i])))@Matrix.Rotation(yaw+math.radians(4*i),4,'Z')@Matrix.Diagonal((w,d,h,1))
    sph=lathe('Coffee_sphere_Z5',[(0,0)]+[(.045*math.sin(math.radians(d)),.045-.045*math.cos(math.radians(d))) for d in range(6,180,6)]+[(0,.09)],mat('Travertine_object_Z5',(.70,.64,.55),.6),S,col)
    sph.matrix_world=Matrix.Translation((base.x+.03,base.y-.02,z+.102))
    bowl=lathe('Coffee_bowl_Z5',[(0,0),(.07,0),(.075,.004),(.135,.035),(.150,.062),(.146,.064),(.128,.040),(.06,.012),(0,.012)],mat('Stoneware_bowl_Z5',(.16,.15,.14),.55),S,col)
    bowl.matrix_world=Matrix.Translation((8.02,2.05,z))
    vase=lathe('Coffee_vase_Z5',[(0,0),(.045,0),(.055,.04),(.058,.10),(.042,.17),(.022,.205),(.024,.22),(.019,.22),(.016,.20),(0,.20)],mat('Glazed_vase_Z5',(.80,.78,.72),.3,coat=.3),S,col)
    vase.matrix_world=Matrix.Translation((7.84,2.55,z))
    log['coffee_objects']=['3 books','travertine sphere','stoneware bowl','glazed vase']
    return log
