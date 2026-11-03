"""Furniture library for the trial CG: imports a model, puts it in metres / Z-up with its footprint centred
on the origin and its feet on z=0, and assigns materials.

Each entry: OBJ path (relative to MODELS dir), unit scale, and a rule mapping object names to materials.
"""
import bpy, math, os
from mathutils import Vector

TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tex')


def oak(name, stain=(0.16, 0.095, 0.06), stain_mix=1.0, grain_scale=1.6, rot=0.0):
    """Oak veneer (Poly Haven, CC0) with an optional dark stain; box-mapped so models without good UVs still read as wood."""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; L = nt.links
    b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (grain_scale, grain_scale, grain_scale); mp.inputs['Rotation'].default_value = (0, 0, rot)
    L.new(tc.outputs['Object'], mp.inputs['Vector'])
    def img(file, colour):
        n = nt.nodes.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(os.path.join(TEX, file), check_existing=True)
        n.image.colorspace_settings.name = 'sRGB' if colour else 'Non-Color'; n.projection = 'BOX'; n.projection_blend = 0.25
        L.new(mp.outputs['Vector'], n.inputs['Vector']); return n
    diff = img('oak_diff_2k.jpg', True); rough = img('oak_rough_2k.jpg', False); nor = img('oak_nor_gl_2k.jpg', False)
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = stain_mix; mix.inputs[7].default_value = (*stain, 1)
    L.new(diff.outputs['Color'], mix.inputs[6]); L.new(mix.outputs[2], b.inputs['Base Color'])
    rr = nt.nodes.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = 0.38; rr.inputs['To Max'].default_value = 0.62
    L.new(rough.outputs['Color'], rr.inputs['Value']); L.new(rr.outputs['Result'], b.inputs['Roughness'])
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 0.6
    L.new(nor.outputs['Color'], nm.inputs['Color']); L.new(nm.outputs['Normal'], b.inputs['Normal'])
    b.inputs['Coat Weight'].default_value = 0.15; b.inputs['Coat Roughness'].default_value = 0.25   # thin oil/lacquer
    return m


def metal(name, colour=(0.02, 0.02, 0.02), rough=0.35):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*colour, 1); b.inputs['Metallic'].default_value = 1; b.inputs['Roughness'].default_value = rough
    return m


def import_obj(path, scale, up='Y', forward='NEGATIVE_Z'):
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=path, global_scale=scale, up_axis=up, forward_axis=forward)
    return [o for o in bpy.data.objects if o not in before and o.type == 'MESH']


def normalise(objs, name):
    """Join into one object, centre the footprint on the origin, put the lowest point on z=0."""
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1: bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active; ob.name = name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    lo = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    hi = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    ob.data.transform(__import__('mathutils').Matrix.Translation(-Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))))
    ob.location = (0, 0, 0)
    bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
    return ob, hi - lo


def androgyne(models_dir, size='150'):
    """Audo Androgyne Dining Table (official 3D, mm, Y-up), dark stained oak top and base."""
    objs = import_obj(os.path.join(models_dir, 'androgyne', 'd' + size, 'androgyne.obj'), 0.001)
    wood = oak('DarkStainedOak'); hw = metal('Hardware')
    for o in objs:
        o.data.materials.clear()
        o.data.materials.append(hw if ('Insert' in o.name or 'Ackurat' in o.name or 'Bracket' in o.name) else wood)
    # the CAD export tessellates the round top coarsely (its rim reads as a polygon); swap only the top disc
    # for a finely divided one of the same diameter, thickness and height
    top = next(o for o in objs if 'Tabletop' in o.name)
    bb = [top.matrix_world @ Vector(c) for c in top.bound_box]
    x0, x1 = min(v.x for v in bb), max(v.x for v in bb); y0, y1 = min(v.y for v in bb), max(v.y for v in bb); z0, z1 = min(v.z for v in bb), max(v.z for v in bb)
    bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=(x1 - x0) / 2, depth=z1 - z0, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    disc = bpy.context.object; disc.data.materials.append(wood)
    bev = disc.modifiers.new('edge', 'BEVEL'); bev.width = 0.002; bev.segments = 2; bev.limit_method = 'ANGLE'
    bpy.ops.object.modifier_apply(modifier='edge')
    objs = [o for o in objs if o is not top] + [disc]; bpy.data.objects.remove(top)
    return normalise(objs, 'Androgyne_' + size)


LIBRARY = {'androgyne_150': lambda d: androgyne(d, '150'), 'androgyne_120': lambda d: androgyne(d, '120')}
