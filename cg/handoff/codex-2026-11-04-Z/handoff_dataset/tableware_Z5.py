"""High-quality procedural tableware (Z5): sculpted sterling-style flatware (rounded sections,
graded thickness, longitudinal sweep, true spoon bowl, four rounded fork tines, thin-edged knife blade)
and saddle-stitched leather placemats. Dimension-based stand-ins; not manufacturer CAD."""
import bpy,bmesh,math
from mathutils import Vector,Matrix
def smooth(a,b,x):
    t=min(max((x-a)/(b-a),0),1);return t*t*(3-2*t)
def lerp(a,b,t):return a+(b-a)*t
def ribbon(name,stations,mat,col,nw=10,bowl=None,cap_start=True,cap_end=True):
    """stations: list of (x,ylo,yhi,zc,thick). Rounded cross-section; optional bowl(x,y)->depth."""
    bm=bmesh.new();top=[];bot=[]
    for (x,ylo,yhi,zc,t) in stations:
        rt=[];rb=[]
        for j in range(nw+1):
            s=j/nw;y=lerp(ylo,yhi,s);u=2*s-1;prof=max(1-u*u,0)**0.5
            d=bowl(x,y) if bowl else 0
            ht=t*0.5*(0.35+0.65*prof);hb=t*0.5*(0.35+0.65*prof)
            rt.append(bm.verts.new((x,y,zc+ht-d)));rb.append(bm.verts.new((x,y,zc-hb-d)))
        top.append(rt);bot.append(rb)
    n=len(stations)
    for i in range(n-1):
        for j in range(nw):
            bm.faces.new((top[i][j],top[i+1][j],top[i+1][j+1],top[i][j+1]))
            bm.faces.new((bot[i][j+1],bot[i+1][j+1],bot[i+1][j],bot[i][j]))
        bm.faces.new((bot[i][0],bot[i+1][0],top[i+1][0],top[i][0]))
        bm.faces.new((top[i][nw],top[i+1][nw],bot[i+1][nw],bot[i][nw]))
    for i,flip in [(0,False),(n-1,True)]:
        if (i==0 and not cap_start) or (i==n-1 and not cap_end):continue
        for j in range(nw):
            f=(top[i][j],top[i][j+1],bot[i][j+1],bot[i][j])
            bm.faces.new(f[::-1] if flip else f)
    bmesh.ops.remove_doubles(bm,verts=bm.verts[:],dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();[setattr(p,'use_smooth',True) for p in me.polygons]
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(mat)
    sd=ob.modifiers.new('sub','SUBSURF');sd.levels=1;sd.render_levels=2
    return ob
def sweep(x,L):          # longitudinal profile: handle end lifted, neck lowest, head slightly up
    return 0.0055*smooth(0.55*L,0,x)**1.6+0.0018*smooth(0.62*L,L,x)**2
def handle_w(x,L,wend,wneck,xneck):
    if x<=0.03:return lerp(wend*0.85,wend,math.sin(min(x/0.03,1)*math.pi/2))
    return lerp(wend,wneck,smooth(0.03,xneck,x))
def knife(name,mat,col):
    L=0.235;xn=0.128;st=[]
    for i in range(141):
        x=L*i/140
        if x<xn:
            w=handle_w(x,L,0.0098,0.0060,xn);ylo,yhi=-w,w;t=lerp(0.0062,0.0042,smooth(0,xn,x))
        else:
            k=(x-xn)/(L-xn);yhi=lerp(0.0055,0.0080,smooth(0,.18,k))-0.0080*(1-max(1-((k-.82)/.18)**2,0)**.5 if k>.82 else 0)
            ylo=-lerp(0.0055,0.0115,smooth(0,.22,k))+0.0115*(1-max(1-((k-.62)/.38)**2,0)**.5 if k>.62 else 0)
            t=lerp(0.0030,0.0013,smooth(0,.25,k))*(1-0.5*smooth(.8,1,k))
        st.append((x,ylo,yhi,sweep(x,L)+0.0031,t))
    return ribbon(name,st,mat,col,12)
def fork(name,mat,col):
    L=0.205;xn=0.118;xr=0.163;st=[]
    for i in range(111):
        x=xr*i/110
        if x<xn:w=handle_w(x,L,0.0112,0.0042,xn);t=lerp(0.0036,0.0022,smooth(0,xn,x))
        else:w=lerp(0.0042,0.0128,smooth(xn,xr,x));t=0.0021
        st.append((x,-w,w,sweep(x,L)+0.0024,t))
    ob=ribbon(name,st,mat,col,12)
    tw=0.0040;gap=(0.0256-4*tw)/3
    for k in range(4):
        y0=-0.0128+k*(tw+gap);ts=[]
        for i in range(41):
            x=xr-0.002+(L-xr+0.002)*i/40;kk=i/40;taper=1-0.30*kk**2;tip=max(1-((kk-.82)/.18)**2,0)**.5 if kk>.82 else 1
            c=y0+tw/2;hw=tw/2*taper*tip
            ts.append((x,c-hw,c+hw,sweep(x,L)+0.0024+0.0012*kk**2,0.0019*(1-0.35*kk)))
        t_ob=ribbon(name+f'_tine{k}',ts,mat,col,6,cap_start=False);t_ob.parent=ob
    return ob
def spoon(name,mat,col):
    L=0.200;xn=0.112;bx=0.163;ba=0.037;bb=0.0215;st=[]
    def bw(x):
        if x<xn:return handle_w(x,L,0.0108,0.0040,xn)
        if x<bx-ba:return lerp(0.0040,0.0060,smooth(xn,bx-ba,x))
        u=(x-bx)/ba;return max(bb*(1-u*u)**0.5*(1.0 if u<0 else 1-0.12*u),0.0005) if abs(u)<1 else 0.0005
    def bowl(x,y):
        u=(x-bx)/ba;v=y/bb
        r=u*u+v*v;return 0.0075*max(1-r,0)**1.2 if r<1 else 0
    for i in range(161):
        x=L*i/160;w=max(bw(x),0.0006)
        t=lerp(0.0034,0.0021,smooth(0,xn,x)) if x<xn else 0.0019
        st.append((x,-w,w,sweep(x,L)+0.0082*smooth(bx-ba*1.1,bx-ba*0.2,x),t))
    return ribbon(name,st,mat,col,14,bowl=bowl)
def silver():
    m=bpy.data.materials.get('Sterling_silver_polished_Z5')
    if m:return m
    m=bpy.data.materials.new('Sterling_silver_polished_Z5');m.use_nodes=True;nt=m.node_tree;b=nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(0.93,0.92,0.90,1);b.inputs['Metallic'].default_value=1;b.inputs['Roughness'].default_value=0.03
    nz=nt.nodes.new('ShaderNodeTexNoise');nz.inputs['Scale'].default_value=900;mr=nt.nodes.new('ShaderNodeMapRange');mr.inputs['To Min'].default_value=0.022;mr.inputs['To Max'].default_value=0.05
    nt.links.new(nz.outputs['Fac'],mr.inputs['Value']);nt.links.new(mr.outputs['Result'],b.inputs['Roughness']);return m
def leather():
    m=bpy.data.materials.get('Leather_placemat_saddle_Z5')
    if m:return m
    m=bpy.data.materials.new('Leather_placemat_saddle_Z5');m.use_nodes=True;nt=m.node_tree;b=nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(0.026,0.018,0.013,1);b.inputs['Roughness'].default_value=0.42;b.inputs['Sheen Weight'].default_value=0.08;b.inputs['Coat Weight'].default_value=0.15;b.inputs['Coat Roughness'].default_value=0.35
    tc=nt.nodes.new('ShaderNodeTexCoord');vor=nt.nodes.new('ShaderNodeTexVoronoi');vor.inputs['Scale'].default_value=1400;vor.feature='DISTANCE_TO_EDGE'
    nt.links.new(tc.outputs['Object'],vor.inputs['Vector']);bp=nt.nodes.new('ShaderNodeBump');bp.inputs['Strength'].default_value=0.25;bp.inputs['Distance'].default_value=0.00015
    nt.links.new(vor.outputs['Distance'],bp.inputs['Height']);nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    nz=nt.nodes.new('ShaderNodeTexNoise');nz.inputs['Scale'].default_value=18;cr=nt.nodes.new('ShaderNodeValToRGB');e=cr.color_ramp.elements;e[0].color=(0.020,0.014,0.010,1);e[1].color=(0.034,0.024,0.017,1)
    nt.links.new(tc.outputs['Object'],nz.inputs['Vector']);nt.links.new(nz.outputs['Fac'],cr.inputs['Fac']);nt.links.new(cr.outputs['Color'],b.inputs['Base Color']);return m
def thread():
    m=bpy.data.materials.get('Leather_stitch_thread_Z5')
    if m:return m
    m=bpy.data.materials.new('Leather_stitch_thread_Z5');m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(0.10,0.075,0.055,1);b.inputs['Roughness'].default_value=0.7;return m
def rounded_rect(w,d,r,n=10):
    pts=[]
    for cx,cy,a0 in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
        for i in range(n+1):a=math.radians(a0+90*i/n);pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    return pts
def placemat(name,col,w=0.46,d=0.34,th=0.003):
    bm=bmesh.new();pts=rounded_rect(w,d,0.012);vs=[bm.verts.new((x,y,0)) for x,y in pts];f=bm.faces.new(vs)
    r=bmesh.ops.extrude_face_region(bm,geom=[f]);bmesh.ops.translate(bm,verts=[v for v in r['geom'] if isinstance(v,bmesh.types.BMVert)],vec=(0,0,th))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(leather());bv=ob.modifiers.new('bv','BEVEL');bv.width=0.0011;bv.segments=4;bv.limit_method='ANGLE';ob.modifiers.new('wn','WEIGHTED_NORMAL')
    [setattr(p,'use_smooth',True) for p in me.polygons]
    # saddle stitch: short raised dashes along an inset path
    path=rounded_rect(w-0.012,d-0.012,0.006,8);segs=[]
    per=[];tot=0
    for a,b in zip(path,path[1:]+path[:1]):l=math.dist(a,b);per.append((a,b,l));tot+=l
    pitch=0.0042;n=int(tot/pitch);bm=bmesh.new();acc=0;k=0;seg=iter(per);a,b,l=next(seg);s0=0
    for i in range(n):
        s=i*pitch
        while s>s0+l:s0+=l;a,b,l=next(seg)
        t=(s-s0)/l;p=(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t);dx,dy=(b[0]-a[0])/l,(b[1]-a[1])/l
        L=0.0027;hw=0.00045
        q=[(p[0]-dx*L/2-dy*hw,p[1]-dy*L/2+dx*hw),(p[0]+dx*L/2-dy*hw,p[1]+dy*L/2+dx*hw),(p[0]+dx*L/2+dy*hw,p[1]+dy*L/2-dx*hw),(p[0]-dx*L/2+dy*hw,p[1]-dy*L/2-dx*hw)]
        v=[bm.verts.new((x,y,th+0.00005)) for x,y in q]+[bm.verts.new((x,y,th+0.00045)) for x,y in q]
        bm.faces.new(v[4:]);[bm.faces.new((v[j],v[(j+1)%4],v[4+(j+1)%4],v[4+j])) for j in range(4)]
    me2=bpy.data.meshes.new(name+'_stitch');bm.to_mesh(me2);bm.free();st=bpy.data.objects.new(name+'_stitch',me2);col.objects.link(st);me2.materials.append(thread());st.parent=ob
    return ob
