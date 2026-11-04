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
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))   # mesh-level, no geometry-nodes asset needed
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


def boucle(name, colour):
    """Chunky bouclé (Safire-like): loop bumps from small Voronoi cells, two-tone yarn, very matte."""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes.new; L = nt.links.new
    b = nt.nodes['Principled BSDF']; tc = N('ShaderNodeTexCoord')
    v = N('ShaderNodeTexVoronoi'); v.feature = 'SMOOTH_F1'; v.inputs['Scale'].default_value = 260; L(tc.outputs['Object'], v.inputs['Vector'])
    n = N('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 420; n.inputs['Detail'].default_value = 4; L(tc.outputs['Object'], n.inputs['Vector'])
    mix = N('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.inputs[6].default_value = (*srgb(colour), 1)
    mix.inputs[7].default_value = (*srgb(tuple(min(255, c * 1.35) for c in colour)), 1)
    th = N('ShaderNodeMapRange'); th.inputs['From Min'].default_value = 0.45; th.inputs['From Max'].default_value = 0.75
    L(n.outputs['Fac'], th.inputs['Value']); L(th.outputs['Result'], mix.inputs[0]); L(mix.outputs[2], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.95; b.inputs['Sheen Weight'].default_value = 0.15; b.inputs['Sheen Roughness'].default_value = 0.6
    b.inputs['Sheen Tint'].default_value = (*srgb(tuple(min(255, c * 1.3) for c in colour)), 1)
    h = N('ShaderNodeMath'); h.operation = 'ADD'; L(v.outputs['Distance'], h.inputs[0]); L(n.outputs['Fac'], h.inputs[1])
    bump = N('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.8; bump.inputs['Distance'].default_value = 0.002
    L(h.outputs[0], bump.inputs['Height']); L(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def plain(name, colour, rough=0.5, metallic=0.0, coat=0.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*srgb(colour), 1); b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metallic; b.inputs['Coat Weight'].default_value = coat
    return m


def _front_to_minus_y(ob, high=0.5):
    """Rotation (Z) that turns a seat so its back (the high part) points to +Y, snapped to 90 degrees."""
    from mathutils import Matrix
    hv = [v.co for v in ob.data.vertices if v.co.z > high]; back = sum(hv, Vector()) / len(hv)
    a = math.atan2(back.y, back.x) - math.radians(90); a = round(a / (math.pi / 2)) * (math.pi / 2)
    return Matrix.Rotation(-a, 4, 'Z')


def eave86_config2(models_dir, colour=(118, 106, 94)):
    """Audo Eave Modular Sofa 86, configuration 2 = Corner + Open Section + Corner (official 3D, cm).
    Audo publishes one corner file; the other end is its mirror image. Upholstered in a Safire-like bouclé."""
    from mathutils import Matrix
    root = os.path.join(models_dir, 'x')
    cloth = boucle('Safire001', colour); glide = plain('Glide', (30, 30, 30), 0.6)
    def module(path, name, rot=None):
        objs = import_obj(path, 0.01)
        for o in objs:
            o.data.materials.clear(); o.data.materials.append(cloth if 'M17050' in o.name and 'Glide' not in o.name else glide)
        ob, dim = normalise(objs, name); rot = rot or _front_to_minus_y(ob); ob.data.transform(rot)
        ob, dim = normalise([ob], name); return ob, dim, rot
    # both files share Audo's CAD frame: take the facing from the symmetric open section and apply it to the corner too
    mid, dm, rot = module(os.path.join(root, 'Eave_Modular_86_Open_Section', '3D', 'Eave Modular 86, Open Section.obj'), 'EaveOpen')
    left, dl, _ = module(os.path.join(root, 'Eave_Modular_86_Corner', '3D', 'Eave Modular 86, Corner.obj'), 'EaveCornerL', rot)
    # make sure the arm of this corner is on its -x side
    arm = [v.co.x for v in left.data.vertices if v.co.z > 0.5 and v.co.y < -0.1]
    if arm and sum(arm) / len(arm) > 0: left.data.transform(Matrix.Scale(-1, 4, (1, 0, 0))); left.data.flip_normals()
    right = left.copy(); right.data = left.data.copy(); bpy.context.collection.objects.link(right)
    right.data.transform(Matrix.Scale(-1, 4, (1, 0, 0))); right.data.flip_normals()
    left.location.x = -(dm.x / 2 + dl.x / 2); right.location.x = dm.x / 2 + dl.x / 2
    for o in (left, mid, right): o.select_set(True)
    return normalise([left, mid, right], 'Eave86_Config2')


def androgyne_lounge(models_dir):
    """Audo Androgyne Lounge Table 120x45 (official 3D, cm): Kunis Breccia top, natural oak base, brass glides."""
    objs = import_obj(os.path.join(models_dir, 'x', 'Androgyne_Lounge_Table_3D', '3D', 'Androgyne_Lounge_Table.obj'), 0.01)
    wood = oak('NaturalOak', **NATURAL_OAK); stone = breccia(); brass = plain('Brass', (190, 150, 95), 0.3, 1.0); hw = metal('Hardware')
    for o in objs:
        o.data.materials.clear()
        o.data.materials.append(stone if 'Stone' in o.name else wood if 'Leg' in o.name else brass if 'Glide' in o.name else hw)
    return normalise(objs, 'AndrogyneLounge')


def plinth(models_dir, kind):
    """Audo Plinth Tall / Cubic (official 3D, mm) in Kunis Breccia."""
    f = {'tall': ('Plinth_Tall_3D', 'Plinth_High.obj'), 'cubic': ('Plinth_Cubic_3D', 'Plinth_Square.obj')}[kind]
    objs = import_obj(os.path.join(models_dir, 'x', f[0], '3D', f[1]), 0.001); stone = breccia()
    for o in objs: o.data.materials.clear(); o.data.materials.append(stone)
    return normalise(objs, 'Plinth_' + kind)


def lathe(name, profile, mats, segments=96):
    """Revolve a list of (radius, z, material_index) points (metres) about Z."""
    import bmesh
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    rings = []
    for r, z, mi in profile:
        ring = [bm.verts.new((r * math.cos(2 * math.pi * k / segments), r * math.sin(2 * math.pi * k / segments), z)) for k in range(segments)]
        rings.append((ring, mi))
    for (a, _), (b_, mi) in zip(rings, rings[1:]):
        for k in range(segments):
            f = bm.faces.new((a[k], a[(k + 1) % segments], b_[(k + 1) % segments], b_[k])); f.material_index = mi; f.smooth = True
    for ring, mi in (rings[0], rings[-1]):
        if ring[0].co.xy.length > 1e-6:
            f = bm.faces.new(ring); f.material_index = mi
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    for m in mats: me.materials.append(m)
    return ob


def beosound_balance(models_dir=None):
    """B&O Beosound Balance, natural oak (no public 3D: modelled from B&O's dimensions 20x20x38 cm and front pack shot)."""
    wood = oak('BeoOak', stain=(1.0, 0.93, 0.84), stain_mix=1.0); cloth = fabric('BalanceFabric', (150, 140, 128), 1400)
    bronze = plain('BalanceBronze', (196, 160, 122), 0.35, 1.0)
    P = [(0.083, 0, 0), (0.095, 0.006, 0), (0.095, 0.124, 0), (0.088, 0.126, 0), (0.066, 0.126, 2), (0.066, 0.13, 2),
         (0.082, 0.138, 2), (0.092, 0.15, 2), (0.0965, 0.157, 1), (0.0965, 0.368, 1), (0.0965, 0.37, 2), (0.0965, 0.38, 2),
         (0.091, 0.38, 2), (0.091, 0.372, 1), (0.0, 0.372, 1)]
    return lathe('BeosoundBalance', P, [wood, cloth, bronze]), Vector((0.193, 0.193, 0.38))


def beolab28(models_dir):
    """B&O BeoLab 28 floor stand, official 3D supplied by the client (mm, Y-up): floor woofer base, tube and the oak
    lamella 'wooden curtain'. Natural aluminium; the tube body behind the curtain is dark."""
    d = os.path.join(models_dir, 'bl28', 'Beolab 28', 'obj')
    alu = plain('NaturalAlu', (200, 200, 198), 0.28, 1.0); dark = plain('Grille', (35, 35, 35), 0.7)
    wood = oak('BeoOak', stain=(1.0, 0.93, 0.84), stain_mix=1.0)
    objs = []
    for f, m in (('beolab-28_woofer_floor.obj', alu), ('beolab-28_tube_basic.obj', None), ('beolab-28_wooden_curtain_off.obj', wood)):
        for o in import_obj(os.path.join(d, f), 0.001):
            o.data.materials.clear()
            if m is not None: o.data.materials.append(m)
            else:
                o.data.materials.append(alu); o.data.materials.append(dark)
                mw = o.matrix_world
                for p in o.data.polygons:                    # speaker body between the base neck and the top cap
                    c = mw @ p.center
                    p.material_index = 1 if 0.44 < c.z < 1.35 else 0
            objs.append(o)
    return normalise(objs, 'BeoLab28')


def _flatten(before):
    """Unparent the meshes an importer just added (keeping their world placement) and drop its empties."""
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == 'MESH']; others = [o for o in new if o.type != 'MESH']
    for o in meshes: mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    for o in others: bpy.data.objects.remove(o)
    return meshes


def lg_g5(models_dir, size='65'):
    """LG OLED evo G5 (LG's own AR model, wall version: 55\" 1222 x 703 x 28 mm). Screen faces -Y."""
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=os.path.join(models_dir, 'lg', 'g5_%s.glb' % size))
    objs = _flatten(before); glass = plain('OLEDOff', (6, 6, 7), 0.05, coat=1.0)
    for o in objs:
        if 'Screen' in o.name:                                   # the AR model ships an artwork on screen; show it switched off
            for i in range(len(o.data.materials)): o.data.materials[i] = glass
    return normalise(objs, 'LG_G5_' + size)


def carrie(models_dir, finish='brushed_brass'):
    """Audo Carrie LED (rechargeable portable lamp by Norm Architects), official 3D (mm), brushed brass."""
    objs = import_obj(os.path.join(models_dir, 'x', 'carrie', '3D', 'Carrie_LED.obj'), 0.001)
    brass = plain('BrushedBrass', (176, 140, 86), 0.32, 1.0)
    for o in objs: o.data.materials.clear(); o.data.materials.append(brass)
    return normalise(objs, 'Carrie')


def hashira_portable(models_dir, finish='raw'):
    """Audo Hashira Table Lamp Portable (Norm Architects), official 3D (mm): raw paper-weave shade on a dark oak foot."""
    objs = import_obj(os.path.join(models_dir, 'x', 'hashira_p', 'Hashira_Table_Lamp_Portable_3D', 'OBJ', 'Hashira _Table_Lamp_Portable.OBJ'), 0.001)
    shade = fabric('HashiraRaw' if finish == 'raw' else 'HashiraWhite', (214, 204, 182) if finish == 'raw' else (236, 234, 228), 700)
    foot = oak('DarkStainedOak', **DARK_OAK)
    for o in objs:
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]; zmax = max(v.z for v in bb); rad = (max(v.x for v in bb) - min(v.x for v in bb)) / 2
        o.data.materials.clear(); o.data.materials.append(shade if zmax > -0.07 and rad > 0.044 else foot)
    return normalise(objs, 'HashiraPortable')


def column_portable(models_dir, finish='aluminium'):
    """Audo Column Table Lamp Portable (Norm Architects), official 3D (m): aluminium or bronzed."""
    objs = import_obj(os.path.join(models_dir, 'x', 'column_p', '3D', 'Column_Table_Lamp.obj'), 1.0)
    m = plain('ColumnAlu', (196, 198, 200), 0.3, 1.0) if finish == 'aluminium' else plain('ColumnBronze', (92, 72, 58), 0.35, 1.0)
    for o in objs: o.data.materials.clear(); o.data.materials.append(m)
    return normalise(objs, 'ColumnPortable')


def glass(name='Glass'):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*srgb((214, 232, 224)), 1); b.inputs['Transmission Weight'].default_value = 1.0
    b.inputs['Roughness'].default_value = 0.0; b.inputs['IOR'].default_value = 1.52
    return m


def brasilia(models_dir):
    """Audo Brasilia Lounge Table 100x100 (official 3D, mm): clear glass top on a natural oak frame.
    The file is one mesh: the 16 mm slab at the top (vertex heights 327-343 mm in the file) is the glass."""
    objs = import_obj(os.path.join(models_dir, 'x', 'brasilia', 'Brasilia Lounge Table 1000x1000_3D', 'OBJ', 'Brasilia Lounge Table 1000x1000.obj'), 0.001)
    ob, dim = normalise(objs, 'Brasilia')
    me = ob.data; me.materials.clear(); me.materials.append(oak('NaturalOak', **NATURAL_OAK)); me.materials.append(glass())
    zt = max(v.co.z for v in me.vertices)
    for p in me.polygons: p.material_index = 1 if min(me.vertices[i].co.z for i in p.vertices) > zt - 0.0165 else 0
    return ob, dim


def androgyne_side50(models_dir):
    """Audo Androgyne Side Table Ø50 (official 3D, mm): Kunis Breccia top, natural oak base."""
    d = os.path.join(models_dir, 'x', 'andro_side50'); f = next(os.path.join(r, n) for r, _, fs in os.walk(d) for n in fs if n.lower().endswith('.obj'))
    objs = import_obj(f, 0.001); wood = oak('NaturalOak', **NATURAL_OAK); stone = breccia(); hw = metal('Hardware')
    for o in objs:
        o.data.materials.clear(); o.data.materials.append(stone if 'Tabletop' in o.name else wood if 'Leg' in o.name else hw)
    return normalise(objs, 'AndrogyneSide50')


def travertine(name='TravertineNeutralWhite', light=(234, 228, 214), dark=(216, 205, 184), pit=(196, 182, 158)):
    """Honed, resin-filled travertine (Gubi 'Neutral White'): fine wavy bedding bands and small pits."""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes.new; L = nt.links.new
    b = nt.nodes['Principled BSDF']; tc = N('ShaderNodeTexCoord')
    warp = N('ShaderNodeTexNoise'); warp.inputs['Scale'].default_value = 4; warp.inputs['Detail'].default_value = 6
    L(tc.outputs['Object'], warp.inputs['Vector'])
    vm = N('ShaderNodeMix'); vm.data_type = 'VECTOR'; vm.inputs[0].default_value = 0.06
    L(tc.outputs['Object'], vm.inputs[4]); L(warp.outputs['Color'], vm.inputs[5])
    # long, thin bedding strata: noise squashed across the layers, low contrast
    mp = N('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.2, 22, 1.2); L(vm.outputs[1], mp.inputs['Vector'])
    band = N('ShaderNodeTexNoise'); band.inputs['Scale'].default_value = 2.2; band.inputs['Detail'].default_value = 9; band.inputs['Roughness'].default_value = 0.62
    L(mp.outputs['Vector'], band.inputs['Vector'])
    ramp = N('ShaderNodeValToRGB'); e = ramp.color_ramp.elements
    e[0].position = 0.35; e[0].color = (*srgb(dark), 1); e[1].position = 0.68; e[1].color = (*srgb(light), 1)
    L(band.outputs['Fac'], ramp.inputs['Fac'])
    pits = N('ShaderNodeTexVoronoi'); pits.inputs['Scale'].default_value = 140; L(vm.outputs[1], pits.inputs['Vector'])
    pm = N('ShaderNodeMapRange'); pm.inputs['From Min'].default_value = 0.03; pm.inputs['From Max'].default_value = 0.09
    L(pits.outputs['Distance'], pm.inputs['Value'])
    col = N('ShaderNodeMix'); col.data_type = 'RGBA'; L(pm.outputs['Result'], col.inputs[0])
    col.inputs[6].default_value = (*srgb(pit), 1); L(ramp.outputs['Color'], col.inputs[7]); L(col.outputs[2], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.55
    bump = N('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.08; L(pm.outputs['Result'], bump.inputs['Height']); L(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def gubi_epic(models_dir, size='large'):
    """GUBI Epic coffee table (GamFratesi), travertine Neutral White. No public 3D: built from Gubi's sizes
    (large Ø110 x H34, small Ø60 x H42) and product photos (3 cm top; hexagonal base about 0.57 / 0.58 of the top
    across its corners)."""
    D, H = {'large': (1.10, 0.34), 'small': (0.60, 0.42), 'medium': (0.80, 0.385)}[size]
    t = 0.03; hexd = D * (0.57 if size == 'large' else 0.58); mat = travertine(); parts = []
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=hexd / 2, depth=H - t, location=(0, 0, (H - t) / 2)); parts.append(bpy.context.object)
    bpy.ops.mesh.primitive_cylinder_add(vertices=192, radius=D / 2, depth=t, location=(0, 0, H - t / 2)); parts.append(bpy.context.object)
    for o in parts:
        o.data.materials.append(mat)
        bev = o.modifiers.new('b', 'BEVEL'); bev.width = 0.0015; bev.segments = 2; bev.limit_method = 'ANGLE'
        bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='b')
    ob, dim = normalise(parts, 'GubiEpic_' + size)
    return ob, dim


def rounded_box(name, w, d, h, z0, r, mat):
    """Box with corners rounded in plan (radius r) and a 2 mm softened edge all round."""
    import bmesh
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w, d, h), verts=bm.verts); bmesh.ops.translate(bm, vec=(0, 0, z0 + h / 2), verts=bm.verts)
    vert_edges = [e for e in bm.edges if abs(e.verts[0].co.x - e.verts[1].co.x) < 1e-6 and abs(e.verts[0].co.y - e.verts[1].co.y) < 1e-6]
    bmesh.ops.bevel(bm, geom=vert_edges, offset=r, segments=12, affect='EDGES', profile=0.5)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    m = o.modifiers.new('soft', 'BEVEL'); m.width = 0.002; m.segments = 2; m.limit_method = 'ANGLE'
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='soft')
    o.data.materials.append(mat); return o


def bolia_eida(models_dir, size=1.0, height=0.28, finish='sand_travertine'):
    """Bolia Eida coffee table (Martin Lauritsen): soft-cornered square top on a central square pedestal.
    No public 3D: built from Bolia's sizes (100x100 / 70x70, H 28 / 32, 2 cm oak top) and the product photos
    (pedestal ~46 % of the top, corner radius ~12 %). Travertine edition: top and pedestal in sand travertine."""
    if finish == 'sand_travertine':
        mat = travertine('TravertineSand', light=(228, 214, 192), dark=(206, 188, 160), pit=(184, 164, 136)); t = 0.03
    else:
        mat = oak('NaturalOak', **NATURAL_OAK); t = 0.02
    base = size * (0.46 if size >= 0.9 else 0.5)
    parts = [rounded_box('eida_base', base, base, height - t, 0, base * 0.12, mat),
             rounded_box('eida_top', size, size, t, height - t, size * 0.12, mat)]
    return normalise(parts, 'Eida_%d_%s' % (round(size * 100), finish))


def potted_plant(models_dir, big=False):
    """Potted Plant 01 (Poly Haven, CC0), tall leafy plant, about 0.6 x 0.6 x 1.35 m.
    The ornate terracotta urn is replaced by a plain cylindrical planter in matte sand ceramic (same height)."""
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=os.path.join(models_dir, 'plant', 'potted_plant_01.gltf'))
    objs = _flatten(before); keep = []
    for o in objs:
        if o.name.startswith('potted_plant_01_pot'): bpy.data.objects.remove(o)
        else: keep.append(o)
    pot = lathe('Planter', [(0.0, 0.0, 0), (0.205, 0.0, 0), (0.215, 0.01, 0), (0.225, 0.52, 0), (0.212, 0.53, 0), (0.212, 0.49, 1), (0.0, 0.49, 1)],
                [plain('PlanterCeramic', (206, 192, 170), 0.75), plain('Soil', (40, 32, 26), 0.95)], 96)
    from mathutils import Matrix
    foliage = [o for o in keep]
    for a in (125, 245):                                       # two more copies of the crown, turned and varied, for a fuller plant
        for o in foliage:
            c = o.copy(); c.data = o.data.copy(); bpy.context.collection.objects.link(c)
            c.matrix_world = Matrix.Rotation(math.radians(a), 4, 'Z') @ Matrix.Scale(0.85 if a == 125 else 0.92, 4) @ o.matrix_world
            keep.append(c)
    ob, dim = normalise(keep + [pot], 'PottedPlant')
    if big:                                                    # a larger specimen: about 1.8 m tall
        ob.data.transform(Matrix.Scale(1.8 / dim.z, 4)); dim = dim * (1.8 / dim.z)
    return ob, dim


def beosound_a9(models_dir):
    """B&O Beosound A9 (5th gen), official 3D supplied by the client (mm; the file stands upside down with the cover
    facing +x). Natural aluminium rim and back, light grey cover (faces whose normal points forward), oak legs."""
    from mathutils import Matrix
    d = os.path.join(models_dir, 'a9')
    objs = import_obj(os.path.join(d, 'beosound_a9_5th_gen.obj'), 0.001, up='Z', forward='Y') + \
           import_obj(os.path.join(d, 'beosound_a9_5th_gen_legs.obj'), 0.001, up='Z', forward='Y')
    alu = plain('NaturalAlu', (200, 200, 198), 0.28, 1.0); cloth = fabric('A9Cover', (200, 198, 192), 1400)
    wood = oak('BeoOak', stain=(1.0, 0.93, 0.84), stain_mix=1.0)
    turn = Matrix.Rotation(math.radians(-90), 4, 'Z') @ Matrix.Rotation(math.pi, 4, 'X')   # stand it up, cover toward -y
    for o in objs:
        o.data.transform(o.matrix_world); o.matrix_world = Matrix(); o.data.transform(turn)
        o.data.materials.clear()
        if 'legs' in o.name: o.data.materials.append(wood); continue
        o.data.materials.append(alu); o.data.materials.append(cloth)
        ymin = min(v.co.y for v in o.data.vertices)
        for p in o.data.polygons:
            p.material_index = 1 if p.normal.y < -0.35 and p.center.y < ymin + 0.09 else 0
    return normalise(objs, 'BeosoundA9')


def ceramic(name, rgb, rough=0.35):
    m = bpy.data.materials.get(name)
    if m: return m
    m = plain(name, rgb, rough); m.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value = 0.3; return m


def _group(parts, name):
    for o in parts: o.select_set(True)
    return normalise(parts, name)


def nn_glaze():
    """Audo New Norm 'Dark Glazed' stoneware: deep brown-charcoal, satin."""
    return ceramic('NewNormDarkGlazed', (62, 54, 48), 0.42)


def place_setting(models_dir=None):
    """One dining place (front = -y), Audo New Norm Dinnerware (Norm Architects) in Dark Glazed: dinner plate Ø27.5 with
    a low bowl Ø13.5 x H5 (Audo's sizes; dinner plate Ø27.5 x H2), New Norm
    cutlery in brushed steel, a plain wine glass and a linen napkin. No public 3D: shapes from Audo's pack shots."""
    g = nn_glaze(); steel = plain('BrushedSteel', (190, 190, 188), 0.32, 1.0); glassm = glass('WineGlass'); linen = fabric('Linen', (196, 186, 168), 900)
    parts = [lathe('nn_plate', [(0, 0.0, 0), (0.117, 0.0, 0), (0.124, 0.003, 0), (0.1375, 0.02, 0), (0.1345, 0.02, 0), (0.122, 0.008, 0), (0.0, 0.006, 0)], [g]),
             lathe('nn_lowbowl', [(0, 0.005, 0), (0.045, 0.005, 0), (0.064, 0.02, 0), (0.0675, 0.055, 0), (0.0645, 0.055, 0), (0.061, 0.022, 0), (0.0, 0.01, 0)], [g]),
             lathe('glass', [(0, 0, 0), (0.036, 0, 0), (0.036, 0.004, 0), (0.004, 0.01, 0), (0.004, 0.11, 0), (0.03, 0.13, 0), (0.042, 0.18, 0), (0.036, 0.22, 0),
                             (0.034, 0.22, 0), (0.039, 0.18, 0), (0.0, 0.122, 0)], [glassm], 64)]
    parts[2].location = (0.14, 0.19, 0)
    for x, l, w in ((-0.165, 0.2, 0.018), (0.165, 0.21, 0.014)):           # fork / knife: slim brushed-steel bars
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -0.01, 0.003)); c = bpy.context.object; c.scale = (w, l, 0.004)
        bpy.ops.object.transform_apply(scale=True); c.data.materials.append(steel); parts.append(c)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.2, 0.0, 0.002)); n = bpy.context.object; n.scale = (0.05, 0.2, 0.004)
    bpy.ops.object.transform_apply(scale=True); n.data.materials.append(linen); parts.append(n)
    return _group(parts, 'PlaceSetting')


def table_centre(models_dir=None):
    """Centre of the dining table: Audo New Norm Fruit Bowl (footed, Ø24.8 x H13, Dark Glazed) with pears."""
    g = nn_glaze(); fruit = plain('Pear', (176, 160, 72), 0.45)
    parts = [lathe('nn_fruitbowl', [(0, 0.0, 0), (0.05, 0.0, 0), (0.05, 0.035, 0), (0.07, 0.04, 0), (0.115, 0.075, 0), (0.124, 0.13, 0),
                                    (0.119, 0.13, 0), (0.11, 0.08, 0), (0.0, 0.045, 0)], [g])]
    for i, (x, y) in enumerate(((-0.04, 0.02), (0.05, -0.01), (0.0, -0.06), (0.04, 0.06))):
        p = lathe('pear%d' % i, [(0, 0.0, 0), (0.03, 0.01, 0), (0.035, 0.035, 0), (0.025, 0.065, 0), (0.016, 0.085, 0), (0.0, 0.095, 0)], [fruit], 32)
        p.location = (x, y, 0.05); p.rotation_euler = (math.radians(20 * (i % 2) - 10), math.radians(15 - 10 * i), 0); parts.append(p)
    return _group(parts, 'TableCentre')


def books_and_vase(models_dir=None):
    """Coffee-table styling: two stacked art books and a small matte vase with a branch."""
    covers = [plain('BookA', (214, 206, 192), 0.8), plain('BookB', (96, 84, 72), 0.8)]; pages = plain('Pages', (236, 232, 222), 0.9)
    parts = []
    for i, (w, d, h, m, a) in enumerate(((0.30, 0.24, 0.035, covers[0], 0), (0.26, 0.21, 0.028, covers[1], 7))):
        z = 0.035 * i
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z + h / 2)); b = bpy.context.object; b.scale = (w, d, h)
        bpy.ops.object.transform_apply(scale=True); b.data.materials.append(m); b.rotation_euler.z = math.radians(a); parts.append(b)
    v = lathe('vase', [(0, 0, 0), (0.05, 0, 0), (0.06, 0.06, 0), (0.045, 0.16, 0), (0.02, 0.2, 0), (0.022, 0.215, 0), (0.0, 0.2, 0)],
              [ceramic('VaseSand', (208, 196, 176), 0.85)], 64)
    v.location = (0.26, 0.04, 0); parts.append(v)
    stem = plain('Branch', (70, 58, 44), 0.8)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.004, depth=0.45, location=(0.27, 0.05, 0.4)); s_ = bpy.context.object
    s_.rotation_euler = (math.radians(8), math.radians(-12), 0); s_.data.materials.append(stem); parts.append(s_)
    return _group(parts, 'BooksVase')


def tray_cups(models_dir=None):
    """Small oak tray with two stoneware cups."""
    wood = oak('NaturalOak', **NATURAL_OAK); cup = ceramic('Stoneware', (226, 220, 208), 0.45)
    parts = [rounded_box('tray', 0.32, 0.22, 0.02, 0.0, 0.03, wood)]
    for x in (-0.06, 0.07):
        c = lathe('cup', [(0, 0.02, 0), (0.03, 0.02, 0), (0.042, 0.03, 0), (0.045, 0.1, 0), (0.042, 0.1, 0), (0.04, 0.035, 0), (0.0, 0.028, 0)], [cup], 48)
        c.location = (x, 0.01 * (x > 0), 0); parts.append(c)
    return _group(parts, 'TrayCups')


def leaf_mat(name='ArecaLeaf'):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes.new; L = nt.links.new
    b = nt.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*srgb((46, 94, 30)), 1); b.inputs['Roughness'].default_value = 0.45
    tr = N('ShaderNodeBsdfTranslucent'); tr.inputs['Color'].default_value = (*srgb((120, 170, 40)), 1)
    mx = N('ShaderNodeMixShader'); mx.inputs[0].default_value = 0.3
    out = nt.nodes['Material Output']; L(b.outputs[0], mx.inputs[1]); L(tr.outputs[0], mx.inputs[2]); L(mx.outputs[0], out.inputs['Surface'])
    return m


def areca_palm(models_dir=None, seed=7):
    """Areca (golden cane) palm in a tapered sand-terracotta pot, after the client's reference photo: about ten
    slender cane stems from one pot, arching pinnate fronds with fine drooping leaflets; overall about 1.9 m.
    Procedural (no suitable free model): pot Ø46/32 x H52."""
    import bmesh, random
    rnd = random.Random(seed)
    stem_m = plain('ArecaCane', (120, 128, 62), 0.6); leaf = leaf_mat()
    pot_m = travertine('TerracottaSand', light=(206, 170, 134), dark=(188, 150, 116), pit=(160, 124, 94))
    pot_m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9
    parts = [lathe('palm_pot', [(0, 0.0, 0), (0.15, 0.0, 0), (0.165, 0.01, 0), (0.215, 0.2, 0), (0.232, 0.42, 0), (0.23, 0.52, 0),
                                (0.215, 0.52, 1), (0.0, 0.49, 1)], [pot_m, plain('PalmSoil', (200, 184, 150), 0.95)], 96)]
    me = bpy.data.meshes.new('palm'); bm = bmesh.new()
    def tube(pts, r0, r1):
        rings = []
        for i, p in enumerate(pts):
            r = r0 + (r1 - r0) * i / (len(pts) - 1); d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
            u = d.orthogonal().normalized(); v = d.cross(u)
            rings.append([bm.verts.new(p + r * (math.cos(a) * u + math.sin(a) * v)) for a in [2 * math.pi * k / 6 for k in range(6)]])
        for a_, b_ in zip(rings, rings[1:]):
            for k in range(6):
                f = bm.faces.new((a_[k], a_[(k + 1) % 6], b_[(k + 1) % 6], b_[k])); f.material_index = 0; f.smooth = True
    def leaflet(base, along, side, length, width, droop):
        pts = []; n = 4
        for i in range(n + 1):
            t = i / n; p = base + side * (length * t) + Vector((0, 0, -droop * t * t)) + along * (0.05 * t)
            pts.append(p)
        vs = []
        for i, p in enumerate(pts):
            w = width * math.sin(math.pi * min(0.95, max(0.08, i / n)))
            vs.append((bm.verts.new(p + along * w / 2), bm.verts.new(p - along * w / 2)))
        for (a1, a2), (b1, b2) in zip(vs, vs[1:]):
            f = bm.faces.new((a1, a2, b2, b1)); f.material_index = 1
    n_stems = 10
    for si in range(n_stems):
        ang = 2 * math.pi * si / n_stems + rnd.uniform(-0.3, 0.3); lean = rnd.uniform(0.1, 0.35)
        h = rnd.uniform(0.75, 1.35); base = Vector((0.05 * math.cos(ang), 0.05 * math.sin(ang), 0.49))
        out = Vector((math.cos(ang), math.sin(ang), 0))
        pts = [base + out * (lean * h * (t ** 1.6)) + Vector((0, 0, h * t)) for t in [k / 8 for k in range(9)]]
        tube(pts, 0.014, 0.008)
        top = pts[-1]
        for fi in range(rnd.randint(2, 4)):
            fa = ang + rnd.uniform(-1.4, 1.4); fdir = Vector((math.cos(fa), math.sin(fa), 0))
            L_ = rnd.uniform(0.55, 0.85); rise = rnd.uniform(0.15, 0.4)
            rach = [top + fdir * (L_ * t) + Vector((0, 0, rise * math.sin(math.pi * t * 0.8) - 0.35 * t * t * L_)) for t in [k / 12 for k in range(13)]]
            tube(rach, 0.006, 0.002)
            for k in range(1, 12):
                p = rach[k]; along = (rach[k + 1] - rach[k - 1]).normalized()
                side0 = along.cross(Vector((0, 0, 1))).normalized()
                for sgn in (1, -1):
                    for j in range(3):
                        tt = (k + j / 3) / 12; q = p + along * (j / 3) * (L_ / 12)
                        length = 0.32 * math.sin(math.pi * min(0.97, 0.12 + tt)) + 0.05
                        side = (side0 * sgn * 0.8 + along * 0.45 + Vector((0, 0, 0.15))).normalized()
                        leaflet(q, along, side, length, 0.018, 0.12 * length / 0.3)
    bm.to_mesh(me); bm.free(); ob = bpy.data.objects.new('palm_foliage', me); bpy.context.collection.objects.link(ob)
    me.materials.append(stem_m); me.materials.append(leaf); parts.append(ob)
    return _group(parts, 'ArecaPalm')


def areca_potted(models_dir):
    """Areca palm (Dypsis lutescens): '[FREE] Dyspis Lutescens - Potted Palm' by AllQuad (Sketchfab, CC BY 4.0).
    Its dark plastic pot is replaced by a tapered sand-terracotta pot after the client's reference (Ø42 top, H46);
    the plant is raised so its base sits at the new soil line."""
    from mathutils import Matrix
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=os.path.join(models_dir, 'areca', 'areca.glb'))
    objs = _flatten(before); keep = []
    for o in objs:
        if 'POT' in o.name.upper() and 'LUTESCENS' not in o.name.upper(): bpy.data.objects.remove(o)
        else:
            o.data.transform(o.matrix_world); o.matrix_world = Matrix(); o.data.transform(Matrix.Translation((0, 0, 0.17))); keep.append(o)
    pot_m = travertine('TerracottaSand', light=(206, 170, 134), dark=(188, 150, 116), pit=(160, 124, 94))
    pot_m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9
    pot = lathe('areca_pot', [(0, 0.0, 0), (0.13, 0.0, 0), (0.145, 0.012, 0), (0.19, 0.16, 0), (0.21, 0.33, 0), (0.21, 0.46, 0),
                              (0.197, 0.46, 1), (0.0, 0.43, 1)], [pot_m, plain('PalmMulch', (196, 180, 146), 0.95)], 96)
    return normalise(keep + [pot], 'ArecaPotted')


def homeview(models_dir):
    """Apple HomeView, tabletop (Apple's own AR model from apple.com, authored in cm)."""
    before = set(bpy.data.objects); bpy.ops.wm.usd_import(filepath=os.path.join(models_dir, 'homeview', 'apple-homeview.usdz'), scale=0.01)
    return normalise(_flatten(before), 'HomeView')


LIBRARY = {'androgyne_150': lambda d: androgyne(d, '150'), 'androgyne_120': lambda d: androgyne(d, '120'),
           'ready_chair': lambda d: ready_chair(d), 'eave86_config2': eave86_config2, 'audo_androgyne_lounge': androgyne_lounge,
           'audo_plinth_tall': lambda d: plinth(d, 'tall'), 'audo_plinth_cubic': lambda d: plinth(d, 'cubic'),
           'beolab28_floor_silver_oak': beolab28, 'beosound_balance_natural_oak': beosound_balance, 'lg_g5_55': lambda d: lg_g5(d, '55'), 'lg_g5_65': lambda d: lg_g5(d, '65'), 'audo_carrie_brushed_brass': carrie, 'polyhaven_potted_plant_01': potted_plant, 'areca_palm': areca_palm, 'areca_potted': areca_potted, 'polyhaven_potted_plant_01_large': lambda d: potted_plant(d, True),
           'tw_place_setting': place_setting, 'tw_table_centre': table_centre, 'tw_books_vase': books_and_vase, 'tw_tray_cups': tray_cups, 'beosound_a9_natural_oak': beosound_a9, 'bolia_eida_100_h28_sand_travertine': lambda d: bolia_eida(d, 1.0, 0.28, 'sand_travertine'),
           'bolia_eida_70_h32_natural_oak': lambda d: bolia_eida(d, 0.7, 0.32, 'natural_oak'), 'gubi_epic_large': lambda d: gubi_epic(d, 'large'), 'gubi_epic_small': lambda d: gubi_epic(d, 'small'), 'audo_brasilia_100_oak_glass': brasilia, 'audo_androgyne_side50': androgyne_side50, 'audo_hashira_portable_raw': hashira_portable, 'audo_column_portable_aluminium': column_portable,
           'audo_column_portable_bronze': lambda d: column_portable(d, 'bronze'), 'apple_homeview': homeview}
