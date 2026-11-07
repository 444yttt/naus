import bpy
from mathutils import Vector,Matrix
def norm_origin(o,scale):
    o.data.transform(Matrix.Scale(scale,4));ps=[v.co for v in o.data.vertices]
    mn=Vector([min(p[i] for p in ps) for i in range(3)]);mx=Vector([max(p[i] for p in ps) for i in range(3)])
    o.data.transform(Matrix.Translation(-Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,mn.z))));o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)
    return mx-mn
# plates
with bpy.data.libraries.load('/work/herm/hdeco_parts.blend') as (s,d):d.objects=[n for n in s.objects if n in('HDeco_all.001','HDeco_all')]
col=bpy.context.scene.collection
names={'HDeco_all.001':'HDeco_presentation_plate_black_D31','HDeco_all':'HDeco_dinner_plate_white_D26'}
for o in d.objects:
    o.name=names[o.name];col.objects.link(o);sz=norm_origin(o,0.31/156.1);print('PLATE',o.name,[round(v,4) for v in sz])
    for m in o.data.materials:
        b=m.node_tree.nodes.get('Principled BSDF')
        if b:b.inputs['Roughness'].default_value=.12;b.inputs['Coat Weight'].default_value=.8;b.inputs['Coat Roughness'].default_value=.04
        if m.name=='black_ceramic' and b:b.inputs['Base Color'].default_value=(.012,.012,.013,1)
        if m.name=='white_ceramic' and b:b.inputs['Base Color'].default_value=(.86,.86,.85,1)
    for m in o.data.materials:
        if m.name in ('Large_round_platter_black','Bread_and_butter_plate_no_1'):
            nt=m.node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');tex.extension='CLIP';tex.interpolation='Cubic'
            tc=nt.nodes.new('ShaderNodeTexCoord');mp=nt.nodes.new('ShaderNodeMapping');mp.inputs['Scale'].default_value=(0.4394,0.4033,1)
            nt.links.new(tc.outputs['UV'],mp.inputs['Vector']);nt.links.new(mp.outputs['Vector'],tex.inputs['Vector'])
            b=nt.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.12;b.inputs['Coat Weight'].default_value=.8;b.inputs['Coat Roughness'].default_value=.04
    [setattr(p,'use_smooth',True) for p in o.data.polygons]
# cutlery
with bpy.data.libraries.load('/work/cut/cutlery_raw.blend') as (s,d2):d2.objects=[n for n in s.objects if n.startswith('pPlane')]
cn={'pPlane1':'Cutlery_dinner_spoon','pPlane2':'Cutlery_dinner_knife','pPlane3':'Cutlery_dinner_fork','pPlane4':'Cutlery_teaspoon'}
sv=bpy.data.materials.new('Sterling_silver_polished');sv.use_nodes=True;nt=sv.node_tree;b=nt.nodes['Principled BSDF']
b.inputs['Base Color'].default_value=(.93,.92,.90,1);b.inputs['Metallic'].default_value=1;b.inputs['Roughness'].default_value=.035
nz=nt.nodes.new('ShaderNodeTexNoise');nz.inputs['Scale'].default_value=60;mr=nt.nodes.new('ShaderNodeMapRange');mr.inputs['To Min'].default_value=.025;mr.inputs['To Max'].default_value=.06;nt.links.new(nz.outputs['Fac'],mr.inputs['Value']);nt.links.new(mr.outputs['Result'],b.inputs['Roughness'])
for o in [x for x in d2.objects if x.type=='MESH']:
    o.parent=None;mw=o.matrix_world.copy();o.data.transform(mw);o.matrix_world=Matrix()
    o.name=cn[o.name];col.objects.link(o);sz=norm_origin(o,0.0195);print('CUT',o.name,[round(v,4) for v in sz])
    o.data.materials.clear();o.data.materials.append(sv);[setattr(p,'use_smooth',True) for p in o.data.polygons]
    sd=o.modifiers.new('sub','SUBSURF');sd.levels=1;sd.render_levels=2
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath='/work/herm/tableware_lib.blend')
