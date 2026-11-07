import sys,os,bpy,bmesh
sys.path.insert(0,'/opt/blender/blender-4.5.9-linux-x64/4.5/scripts/addons_core')
from io_scene_fbx import parse_fbx
root,ver=parse_fbx.parse('/work/herm/x/h/model/fbx/h-deco_tableware_hermes_fbx.FBX')
def find(e,i):return next((c for c in e.elems if c.id==i),None)
def arr(n):
    p=n.props
    return list(p[0]) if len(p)==1 and hasattr(p[0],'__len__') and not isinstance(p[0],bytes) else list(p)
objs=find(root,b'Objects');conn=find(root,b'Connections')
nm=lambda e:e.props[0].split(b'\x00')[0].decode(errors='replace')
model=[e for e in objs.elems if e.id==b'Model'][0]
V=arr(find(model,b'Vertices'));PI=arr(find(model,b'PolygonVertexIndex'))
uvl=find(model,b'LayerElementUV');uv=arr(find(uvl,b'UV'));uvi=find(uvl,b'UVIndex');uvi=arr(uvi) if uvi else None
print('UV map',find(uvl,b'MappingInformationType').props[0],find(uvl,b'ReferenceInformationType').props[0])
mel=find(model,b'LayerElementMaterial');mats=arr(find(mel,b'Materials'));print('MAT map',find(mel,b'MappingInformationType').props[0])
# polygons
polys=[];cur=[]
for i in PI:
    if i<0:cur.append(-i-1);polys.append(cur);cur=[]
    else:cur.append(i)
print('verts',len(V)//3,'polys',len(polys),'loops',len(PI))
# material order: connections Model<-Material (OO, child=material, parent=model) in order
mat_names=[];tex_of={}
textures={nm(e):e for e in objs.elems if e.id==b'Texture'};materials={nm(e):e for e in objs.elems if e.id==b'Material'}
for c in conn.elems:
    p=c.props
    if p[0]!=b'OO' and p[0]!=b'OP':continue
    a=p[1].split(b'\x00')[0].decode(errors='replace');b=p[2].split(b'\x00')[0].decode(errors='replace')
    if a in materials and b==nm(model):mat_names.append(a)
    if a in textures and b in materials:tex_of.setdefault(b,[]).append((a,p[3].decode() if len(p)>3 else ''))
videos={nm(e):e for e in objs.elems if e.id==b'Video'}
vid_of={}
for c in conn.elems:
    p=c.props
    if p[0] in (b'OO',b'OP'):
        a=p[1].split(b'\x00')[0].decode(errors='replace');b2=p[2].split(b'\x00')[0].decode(errors='replace')
        if a in videos and b2 in textures:vid_of[b2]=a
def _fn(e):
    for key in (b'RelativeFilename',b'FileName',b'Filename'):
        f=find(e,key)
        if f and f.props and f.props[0]:
            s=f.props[0].decode(errors='replace').replace('\\','/');
            if s.strip():return os.path.basename(s)
    return None
def texfile(t):
    f=_fn(textures[t])
    if not f and t in vid_of:f=_fn(videos[vid_of[t]])
    return f
me=bpy.data.meshes.new('HDeco_all');sc=1
me.from_pydata([(V[3*i]*sc,V[3*i+1]*sc,V[3*i+2]*sc) for i in range(len(V)//3)],[],polys)
uvlay=me.uv_layers.new(name='UV')
for li in range(len(me.loops)):
    k=uvi[li] if uvi else li;uvlay.data[li].uv=(uv[2*k],uv[2*k+1])
M='/work/herm/x/h/model/Maps/'
for n in mat_names:
    m=bpy.data.materials.new(n);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF']
    for t,prop in tex_of.get(n,[]):
        f=texfile(t);path=M+f if f and os.path.exists(M+f) else None
        print('MATTEX',n,t,prop,f,bool(path))
        if path and ('diffuse' in prop.lower() or prop==''):
            tn=m.node_tree.nodes.new('ShaderNodeTexImage');tn.image=bpy.data.images.load(path,check_existing=True);m.node_tree.links.new(tn.outputs['Color'],b.inputs['Base Color'])
    me.materials.append(m)
for i,p in enumerate(me.polygons):p.material_index=mats[i] if len(mats)>1 else mats[0]
me.validate();ob=bpy.data.objects.new('HDeco_all',me);bpy.context.scene.collection.objects.link(ob)
print('MATS',mat_names)
bpy.ops.wm.save_as_mainfile(filepath='/work/herm/hdeco_all.blend')
