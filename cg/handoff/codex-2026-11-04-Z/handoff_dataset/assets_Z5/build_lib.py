import bpy,os
from mathutils import Vector
T='/work/plant2/x/textures/'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath='/work/plant2/x/source/Plants.fbx')
# relink textures
miss=[]
for im in bpy.data.images:
    base=os.path.basename(im.filepath);stem,ext=os.path.splitext(base)
    cand=[T+base]+[T+stem+e for e in ('.jpg','.png','.tif')]
    ok=next((c for c in cand if os.path.exists(c)),None)
    if ok:im.filepath=ok;im.reload()
    else:miss.append(base)
print('MISSING',miss)
for m in bpy.data.materials:
    if not m.use_nodes:continue
    nt=m.node_tree;b=nt.nodes.get('Principled BSDF')
    if not b:continue
    # drop broken alpha links to missing images; link PNG alpha for leaves
    for l in list(b.inputs['Alpha'].links):
        if l.from_node.type=='TEX_IMAGE' and (not l.from_node.image or not os.path.exists(l.from_node.image.filepath)):nt.links.remove(l)
    if m.name in('Leaf1','Leaf2','Monstera'):
        src=b.inputs['Base Color'].links[0].from_node
        while src.type!='TEX_IMAGE':src=[i for i in src.inputs if i.is_linked][0].links[0].from_node
        nt.links.new(src.outputs['Alpha'],b.inputs['Alpha']);src.image.alpha_mode='STRAIGHT'
    m.blend_method='HASHED'
    b.inputs['Alpha'].default_value=1.0
for o in list(bpy.context.scene.objects):
    if o.type!='MESH':continue
    o.select_set(True)
bpy.ops.object.select_all(action='DESELECT')
for o in [o for o in bpy.context.scene.objects if o.type=='MESH']:
    o.parent=None
for o in [o for o in bpy.context.scene.objects if o.type=='MESH']:
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);o.select_set(False)
    s=0.181;o.scale=(s,s,s);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.select_set(False)
    # origin to bottom centre
    pts=[o.matrix_world@v.co for v in o.data.vertices];mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)));mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    c=Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,mn.z));o.data.transform(__import__('mathutils').Matrix.Translation(-(c-o.location)));o.location=(0,0,0)
    print('PLANT',o.name,[round(v,3) for v in (mx-mn)])
for o in [o for o in bpy.context.scene.objects if o.type!='MESH']:bpy.data.objects.remove(o)
for m in bpy.data.materials:
    if m.use_nodes:
        for n in list(m.node_tree.nodes):
            if n.type=='TEX_IMAGE' and n.image and not os.path.exists(n.image.filepath):m.node_tree.nodes.remove(n)
for im in list(bpy.data.images):
    if im.filepath and not os.path.exists(im.filepath):bpy.data.images.remove(im)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath='/work/plant2/plants_lib.blend')
