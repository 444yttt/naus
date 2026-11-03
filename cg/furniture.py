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


def srgb(c):
    return tuple(((v / 255) / 12.92) if v / 255 <= 0.04045 else (((v / 255) + 0.055) / 1.055) ** 2.4 for v in c)


def breccia(name='KunisBreccia'):
    """Honed Kunis Breccia (sand): angular beige clasts in a slightly darker matrix, fine grain and a few pores.
    Procedural so it has no visible repeat on a 1.5 m top; colours sampled from Audo's own pack shot."""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes.new; L = nt.links.new
    b = nt.nodes['Principled BSDF']
    tc = N('ShaderNodeTexCoord')
    warp = N('ShaderNodeTexNoise'); warp.inputs['Scale'].default_value = 6; warp.inputs['Detail'].default_value = 3
    L(tc.outputs['Object'], warp.inputs['Vector'])
    wv = N('ShaderNodeMix'); wv.data_type = 'VECTOR'; wv.inputs[0].default_value = 0.025
    L(tc.outputs['Object'], wv.inputs[4]); L(warp.outputs['Color'], wv.inputs[5])
    def vor(scale, feature='F1'):
        v = N('ShaderNodeTexVoronoi'); v.feature = feature; v.inputs['Scale'].default_value = scale; v.inputs['Randomness'].default_value = 1
        L(wv.outputs[1], v.inputs['Vector']); return v
    big = vor(16); small = vor(110)
    pal = [(198, 179, 156), (189, 168, 143), (206, 189, 168), (180, 159, 135), (194, 175, 153)]
    def ramp(src):
        r = N('ShaderNodeValToRGB'); r.color_ramp.interpolation = 'CONSTANT'; els = r.color_ramp.elements
        els[0].position = 0; els[0].color = (*srgb(pal[0]), 1); els[1].position = 0.2; els[1].color = (*srgb(pal[1]), 1)
        for i, c in enumerate(pal[2:]):
            e = els.new(0.4 + 0.2 * i); e.color = (*srgb(c), 1)
        sep = N('ShaderNodeSeparateColor'); L(src.outputs['Color'], sep.inputs['Color']); L(sep.outputs[0], r.inputs['Fac']); return r
    rb = ramp(big); rs = ramp(small)
    # small fragments show through inside the big clasts where a second random channel says so
    sep2 = N('ShaderNodeSeparateColor'); L(small.outputs['Color'], sep2.inputs['Color'])
    gate = N('ShaderNodeMath'); gate.operation = 'GREATER_THAN'; gate.inputs[1].default_value = 0.8; L(sep2.outputs[1], gate.inputs[0])
    c1 = N('ShaderNodeMix'); c1.data_type = 'RGBA'; L(gate.outputs[0], c1.inputs[0]); L(rb.outputs['Color'], c1.inputs[6]); L(rs.outputs['Color'], c1.inputs[7])
    # matrix seams between clasts
    edge = vor(16, 'DISTANCE_TO_EDGE')
    seam = N('ShaderNodeMapRange'); seam.inputs['From Min'].default_value = 0.0; seam.inputs['From Max'].default_value = 0.012; seam.inputs['To Min'].default_value = 0.55
    L(edge.outputs['Distance'], seam.inputs['Value'])
    c2 = N('ShaderNodeMix'); c2.data_type = 'RGBA'; L(seam.outputs['Result'], c2.inputs[0])
    c2.inputs[6].default_value = (*srgb((172, 152, 128)), 1); L(c1.outputs[2], c2.inputs[7])
    # grain and pores
    grain = N('ShaderNodeTexNoise'); grain.inputs['Scale'].default_value = 900; grain.inputs['Detail'].default_value = 2
    L(tc.outputs['Object'], grain.inputs['Vector'])
    g = N('ShaderNodeMix'); g.data_type = 'RGBA'; g.blend_type = 'OVERLAY'; g.inputs[0].default_value = 0.12
    L(c2.outputs[2], g.inputs[6]); L(grain.outputs['Color'], g.inputs[7])
    pore_n = N('ShaderNodeTexVoronoi'); pore_n.inputs['Scale'].default_value = 260; L(tc.outputs['Object'], pore_n.inputs['Vector'])
    pore = N('ShaderNodeMapRange'); pore.inputs['From Min'].default_value = 0.035; pore.inputs['From Max'].default_value = 0.07
    L(pore_n.outputs['Distance'], pore.inputs['Value'])
    c3 = N('ShaderNodeMix'); c3.data_type = 'RGBA'; L(pore.outputs['Result'], c3.inputs[0])
    c3.inputs[6].default_value = (*srgb((122, 102, 82)), 1); L(g.outputs[2], c3.inputs[7])
    mot = N('ShaderNodeTexNoise'); mot.inputs['Scale'].default_value = 3.5; mot.inputs['Detail'].default_value = 4
    L(tc.outputs['Object'], mot.inputs['Vector'])
    c4 = N('ShaderNodeMix'); c4.data_type = 'RGBA'; c4.blend_type = 'SOFT_LIGHT'; c4.inputs[0].default_value = 0.25
    L(c3.outputs[2], c4.inputs[6]); L(mot.outputs['Color'], c4.inputs[7])
    L(c4.outputs[2], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.5
    bump = N('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.05; bump.inputs['Distance'].default_value = 0.0005
    L(pore.outputs['Result'], bump.inputs['Height']); L(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def fabric(name, colour, scale=900):
    """Fine woven wool upholstery (warp/weft ribs plus slub noise), matte."""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes.new; L = nt.links.new
    b = nt.nodes['Principled BSDF']; tc = N('ShaderNodeTexCoord')
    def wave(axis):
        w = N('ShaderNodeTexWave'); w.bands_direction = axis; w.inputs['Scale'].default_value = scale
        w.inputs['Distortion'].default_value = 2; w.inputs['Detail'].default_value = 1; L(tc.outputs['Object'], w.inputs['Vector']); return w
    wx = wave('X'); wy = wave('Y')
    mul = N('ShaderNodeMath'); mul.operation = 'MULTIPLY'; L(wx.outputs['Fac'], mul.inputs[0]); L(wy.outputs['Fac'], mul.inputs[1])
    slub = N('ShaderNodeTexNoise'); slub.inputs['Scale'].default_value = 140; slub.inputs['Detail'].default_value = 6; L(tc.outputs['Object'], slub.inputs['Vector'])
    base = N('ShaderNodeMix'); base.data_type = 'RGBA'; base.blend_type = 'OVERLAY'; base.inputs[0].default_value = 0.22
    base.inputs[6].default_value = (*srgb(colour), 1); L(slub.outputs['Color'], base.inputs[7])
    dark = N('ShaderNodeMix'); dark.data_type = 'RGBA'; dark.blend_type = 'MULTIPLY'
    inv = N('ShaderNodeMapRange'); inv.inputs['To Min'].default_value = 0.85; inv.inputs['To Max'].default_value = 1.0; L(mul.outputs[0], inv.inputs['Value'])
    L(inv.outputs['Result'], dark.inputs[0]); dark.inputs[0].default_value = 1
    dark.inputs[0].default_value = 1; L(base.outputs[2], dark.inputs[6])
    gray = N('ShaderNodeCombineColor'); L(inv.outputs['Result'], gray.inputs[0]); L(inv.outputs['Result'], gray.inputs[1]); L(inv.outputs['Result'], gray.inputs[2])
    L(gray.outputs['Color'], dark.inputs[7]); L(dark.outputs[2], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.92; b.inputs['Sheen Weight'].default_value = 0.35; b.inputs['Sheen Roughness'].default_value = 0.5
    bump = N('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.35; bump.inputs['Distance'].default_value = 0.0004
    L(mul.outputs[0], bump.inputs['Height']); L(bump.outputs['Normal'], b.inputs['Normal'])
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


NATURAL_OAK = dict(stain=(1.0, 0.80, 0.60), stain_mix=1.0)   # clear oil warms the raw veneer (matched to Audo pack shot)
DARK_OAK = dict(stain=(0.16, 0.095, 0.06), stain_mix=1.0)


def androgyne(models_dir, size='150', base='natural', top='sand'):
    """Audo Androgyne Dining Table (official 3D, mm, Y-up). base: natural|dark oak; top: sand (Kunis Breccia)|natural|dark."""
    objs = import_obj(os.path.join(models_dir, 'androgyne', 'd' + size, 'androgyne.obj'), 0.001)
    finish = {'natural': ('NaturalOak', NATURAL_OAK), 'dark': ('DarkStainedOak', DARK_OAK)}
    wood = oak(finish[base][0], **finish[base][1]); hw = metal('Hardware')
    top_mat = breccia() if top == 'sand' else oak(finish[top][0], **finish[top][1])
    for o in objs:
        o.data.materials.clear()
        o.data.materials.append(hw if ('Insert' in o.name or 'Ackurat' in o.name or 'Bracket' in o.name) else wood)
    # the CAD export tessellates the round top coarsely (its rim reads as a polygon); swap only the top disc
    # for a finely divided one of the same diameter, thickness and height
    top = next(o for o in objs if 'Tabletop' in o.name)
    bb = [top.matrix_world @ Vector(c) for c in top.bound_box]
    x0, x1 = min(v.x for v in bb), max(v.x for v in bb); y0, y1 = min(v.y for v in bb), max(v.y for v in bb); z0, z1 = min(v.z for v in bb), max(v.z for v in bb)
    bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=(x1 - x0) / 2, depth=z1 - z0, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    disc = bpy.context.object; disc.data.materials.append(top_mat)
    bev = disc.modifiers.new('edge', 'BEVEL'); bev.width = 0.002; bev.segments = 2; bev.limit_method = 'ANGLE'
    bpy.ops.object.modifier_apply(modifier='edge')
    objs = [o for o in objs if o is not top] + [disc]; bpy.data.objects.remove(top)
    return normalise(objs, 'Androgyne_' + size)


def ready_chair(models_dir, colour=(203, 199, 186)):
    """Audo Ready Dining Chair, seat upholstered (official 3D), natural oak, Hallingdal 65 200.
    The CAD export is one unlabeled surface soup, so the seat pad is found by layering: in the seat zone, where a vertical
    ray crosses more than the shell's two surfaces, faces above the shell top are the pad (checked in a red/grey test render)."""
    from mathutils.bvhtree import BVHTree
    path = os.path.join(models_dir, 'ready', 'Ready_Dining_Chair_3D', 'Ready_Dining_Chair_Seat_Upholstered', 'Ready_Dining_Chair_Seat_Upholstered.obj')
    objs = import_obj(path, 0.001)
    ob, dim = normalise(objs, 'ReadyChair')        # front edge at -y, back rest at +y
    me = ob.data; tree = BVHTree.FromPolygons([v.co for v in me.vertices], [p.vertices for p in me.polygons])
    y0 = min(v.co.y for v in me.vertices)
    wood = oak('NaturalOak', **NATURAL_OAK); cloth = fabric('Hallingdal65_200', colour)
    me.materials.clear(); me.materials.append(wood); me.materials.append(cloth)
    def layers(x, y):
        zs, z = [], -0.1
        while True:
            hit = tree.ray_cast(Vector((x, y, z)), Vector((0, 0, 1)))
            if hit[0] is None: return zs
            if not zs or hit[0].z - zs[-1] > 0.0015: zs.append(hit[0].z)
            z = hit[0].z + 0.0005
    for p in me.polygons:
        c = p.center
        vz = [me.vertices[i].co for i in p.vertices]
        if max(v.y for v in vz) - y0 > 0.40 or max(v.z for v in vz) > 0.495 or c.z < 0.3: p.material_index = 0; continue
        q = c - p.normal * 0.003 if abs(p.normal.z) < 0.5 else c      # look just inside a side face
        zs = [z for z in layers(q.x, q.y) if z > 0.3]
        # bare shell = 2 surfaces; seat with pad = shell bottom, shell top, (pad bottom), pad top
        p.material_index = 1 if len(zs) >= 3 and c.z > zs[1] + 0.001 else 0
    return ob, dim


LIBRARY = {'androgyne_150': lambda d: androgyne(d, '150'), 'androgyne_120': lambda d: androgyne(d, '120'),
           'ready_chair': lambda d: ready_chair(d)}
