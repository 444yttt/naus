"""
NAUS - Chidorigafuchi living room (Blender 4.2 LTS)

Run: Scripting tab > Open > build_room.py > Run Script (▶).
Structure only by default (WITH_VIEW = False). Set WITH_VIEW = True and put trees.jpg
next to this script to add the view outside the window.
Units: metres. Z up. The camera stands at the photo position looking toward the window (+Y).
Dimensions are estimated from photos.
"""
import bpy, bmesh, os, math

# ---------------------------------------------------------------- dimensions
EYE = 1.22            # camera height
W = 3.12              # half room width
Y0, YW = -1.6, 7.0    # room: back (behind camera) .. window wall
H = 2.40              # soffit (lowered ceiling) height
HC = 2.55             # raised coffer height
CX, CY1 = 1.80, 4.70  # coffer half width, coffer far edge
OX, OH = 2.62, 2.19   # window opening half width / height
YB = 9.30             # balcony depth (railing line)
MULLIONS = [-1.72, -0.56, 0.56, 1.70]
T = 0.10              # wall thickness
WITH_VIEW = False     # exterior view image outside the window (off while building the structure)

# ---------------------------------------------------------------- reset scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
for blocks in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.images):
    for b in list(blocks):
        if b.users == 0:
            blocks.remove(b)

scene = bpy.context.scene
def coll(name):
    c = bpy.data.collections.new(name); scene.collection.children.link(c); return c
C_ROOM, C_WIN, C_BAL, C_LIGHT, C_EXT = (coll(n) for n in ("Room", "Window", "Balcony", "Lights", "Exterior"))

# ---------------------------------------------------------------- materials
def principled(name, color, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m, b

def tex_coord(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord"); return tc.outputs["Object"]

def mat_wood():
    m, b = principled("WalnutFloor", (0.06, 0.03, 0.02), 0.28)
    nt = m.node_tree; L = nt.links; co = tex_coord(nt)
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Brick Width"].default_value = 2.4; brick.inputs["Row Height"].default_value = 0.20
    brick.inputs["Mortar Size"].default_value = 0.002; brick.offset = 0.37
    brick.inputs["Color1"].default_value = (0.075, 0.040, 0.026, 1); brick.inputs["Color2"].default_value = (0.050, 0.026, 0.017, 1)
    brick.inputs["Mortar"].default_value = (0.012, 0.007, 0.005, 1)
    wave = nt.nodes.new("ShaderNodeTexWave"); wave.wave_type = 'BANDS'; wave.bands_direction = 'Y'
    wave.inputs["Scale"].default_value = 18; wave.inputs["Distortion"].default_value = 6; wave.inputs["Detail"].default_value = 3
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs["Factor"].default_value = 0.35
    ramp = nt.nodes.new("ShaderNodeMapRange"); ramp.inputs["To Min"].default_value = 0.75
    L.new(co, brick.inputs["Vector"]); L.new(co, wave.inputs["Vector"])
    L.new(wave.outputs["Fac"], ramp.inputs["Value"])
    L.new(brick.outputs["Color"], mix.inputs[6]); L.new(ramp.outputs["Result"], mix.inputs[7])
    L.new(mix.outputs[2], b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.15
    L.new(brick.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m

def mat_speckle(name, base, dark, rough, scale):
    m, b = principled(name, base, rough); nt = m.node_tree; L = nt.links
    vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = scale
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'
    mix.inputs[6].default_value = (*base, 1); mix.inputs[7].default_value = (*dark, 1)   # colour A/B
    L.new(tex_coord(nt), vor.inputs["Vector"]); L.new(vor.outputs["Distance"], mix.inputs["Factor"])
    L.new(mix.outputs[2], b.inputs["Base Color"])
    return m

def mat_tile():
    m, b = principled("BalconyTile", (0.35, 0.36, 0.37), 0.7); nt = m.node_tree; L = nt.links
    brick = nt.nodes.new("ShaderNodeTexBrick"); brick.offset = 0.0
    brick.inputs["Brick Width"].default_value = 0.6; brick.inputs["Row Height"].default_value = 0.6
    brick.inputs["Mortar Size"].default_value = 0.006
    brick.inputs["Color1"].default_value = (0.36, 0.37, 0.38, 1); brick.inputs["Color2"].default_value = (0.33, 0.34, 0.35, 1)
    brick.inputs["Mortar"].default_value = (0.15, 0.15, 0.15, 1)
    L.new(tex_coord(nt), brick.inputs["Vector"]); L.new(brick.outputs["Color"], b.inputs["Base Color"])
    return m

def mat_emit(name, color, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (*color, 1); e.inputs["Strength"].default_value = strength
    nt.links.new(e.outputs["Emission"], nt.nodes["Material Output"].inputs["Surface"])
    return m

def mat_glass(name, color=(0.92, 0.97, 0.96)):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    g = nt.nodes.new("ShaderNodeBsdfGlass"); g.inputs["Color"].default_value = (*color, 1)
    g.inputs["Roughness"].default_value = 0.0; g.inputs["IOR"].default_value = 1.45
    nt.links.new(g.outputs["BSDF"], nt.nodes["Material Output"].inputs["Surface"])
    return m

M = {
    "floor": mat_wood(),
    "wall": principled("Wall", (0.62, 0.57, 0.49), 0.9)[0],
    "ceil": principled("Ceiling", (0.78, 0.75, 0.69), 0.95)[0],
    "alu": principled("AluminiumDark", (0.025, 0.025, 0.028), 0.35, 0.8)[0],
    "steel": principled("Steel", (0.75, 0.76, 0.78), 0.25, 1.0)[0],
    "granite": mat_speckle("Granite", (0.42, 0.41, 0.39), (0.12, 0.12, 0.12), 0.55, 220),
    "tile": mat_tile(),
    "soffit": principled("BalconySoffit", (0.45, 0.46, 0.45), 0.85)[0],
    "glass": mat_glass("Glass"),
    "led": mat_emit("CoveLED", (1.0, 0.52, 0.18), 45.0),
    "dl": mat_emit("DownlightLens", (1.0, 0.85, 0.65), 25.0),
    "ac": principled("AirCon", (0.82, 0.81, 0.78), 0.5)[0],
    "vent": principled("Vent", (0.08, 0.08, 0.08), 0.6)[0],
}

# ---------------------------------------------------------------- geometry helpers
def box(name, x0, x1, y0, y1, z0, z1, mat, c):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    v = [bm.verts.new((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    me.materials.append(mat); o = bpy.data.objects.new(name, me); c.objects.link(o); return o

# ---------------------------------------------------------------- room shell
box("Floor", -W, W, Y0, YW, -0.05, 0, M["floor"], C_ROOM)
box("WallLeft", -W - T, -W, Y0, YW, 0, HC + 0.05, M["wall"], C_ROOM)
box("WallRight", W, W + T, Y0, YW, 0, HC + 0.05, M["wall"], C_ROOM)
box("WallBehindCamera", -W, W, Y0 - T, Y0, 0, HC + 0.05, M["wall"], C_ROOM)
box("BackWallL", -W, -OX, YW, YW + T, 0, H, M["wall"], C_ROOM)
box("BackWallR", OX, W, YW, YW + T, 0, H, M["wall"], C_ROOM)
box("BackWallTop", -OX, OX, YW, YW + T, OH, H, M["wall"], C_ROOM)
for n, x0, x1 in (("BaseboardL", -W, -W + .012), ("BaseboardR", W - .012, W)):
    box(n, x0, x1, Y0, YW, 0, .06, M["wall"], C_ROOM)

# ceiling: soffit ring at H around a raised coffer at HC, with cove fascia + hidden LED strips
box("SoffitL", -W, -CX, Y0, YW, H, H + .05, M["ceil"], C_ROOM)
box("SoffitR", CX, W, Y0, YW, H, H + .05, M["ceil"], C_ROOM)
box("SoffitBack", -CX, CX, CY1, YW, H, H + .05, M["ceil"], C_ROOM)
box("CofferCeiling", -W, W, Y0, YW, HC, HC + .05, M["ceil"], C_ROOM)
box("CofferFasciaL", -CX - .03, -CX, Y0, CY1 + .03, H, H + .08, M["ceil"], C_ROOM)
box("CofferFasciaR", CX, CX + .03, Y0, CY1 + .03, H, H + .08, M["ceil"], C_ROOM)
box("CofferFasciaBack", -CX - .03, CX + .03, CY1, CY1 + .03, H, H + .08, M["ceil"], C_ROOM)
box("CoveLED_L", -CX - .14, -CX - .10, Y0, CY1 + .1, H + .05, H + .065, M["led"], C_LIGHT)
box("CoveLED_R", CX + .10, CX + .14, Y0, CY1 + .1, H + .05, H + .065, M["led"], C_LIGHT)
box("CoveLED_Back", -CX - .1, CX + .1, CY1 + .10, CY1 + .14, H + .05, H + .065, M["led"], C_LIGHT)

# downlights (lens + spot light)
for i, (x, y) in enumerate([(-1.58, 5.5), (0.02, 5.5), (1.64, 5.5), (-2.7, 3.1), (2.7, 3.1), (-2.7, 0.6), (2.7, 0.6)]):
    box(f"Downlight{i}", x - .045, x + .045, y - .045, y + .045, H - .004, H, M["dl"], C_LIGHT)
    ld = bpy.data.lights.new(f"DownlightSpot{i}", 'SPOT'); ld.energy = 18; ld.color = (1.0, 0.84, 0.66)
    ld.spot_size = math.radians(70); ld.spot_blend = 0.6; ld.shadow_soft_size = 0.03
    lo = bpy.data.objects.new(f"DownlightSpot{i}", ld); lo.location = (x, y, H - .01); C_LIGHT.objects.link(lo)

# air-conditioner cassette (seen in the photos)
box("AirCon", -2.5, -2.0, 1.2, 2.35, H - .16, H, M["ac"], C_ROOM)
box("AirConVent", -2.43, -2.07, 1.3, 2.25, H - .165, H - .16, M["vent"], C_ROOM)

# ---------------------------------------------------------------- window wall
yF = YW + .03
for i, x in enumerate(MULLIONS):
    box(f"Mullion{i}", x - .04, x + .04, yF - .05, yF + .05, 0, OH, M["alu"], C_WIN)
box("FrameL", -OX - .02, -OX + .06, yF - .07, yF + .07, 0, OH, M["alu"], C_WIN)
box("FrameR", OX - .06, OX + .02, yF - .07, yF + .07, 0, OH, M["alu"], C_WIN)
box("FrameTop", -OX, OX, yF - .07, yF + .07, OH - .06, OH, M["alu"], C_WIN)
box("FrameSill", -OX, OX, yF - .07, yF + .07, 0, .025, M["alu"], C_WIN)
edges = [-OX + .06, *MULLIONS, OX - .06]
for i in range(len(edges) - 1):
    box(f"Glass{i}", edges[i] + .04, edges[i + 1] - .04, yF - .006, yF + .006, .025, OH - .06, M["glass"], C_WIN)
for i, x in enumerate((-2.3, 2.3)):   # sliding-door pulls
    box(f"Pull{i}", x - .012, x + .012, yF - .09, yF - .07, .9, 1.25, M["alu"], C_WIN)

# ---------------------------------------------------------------- balcony
box("BalconyFloor", -OX, OX, YW + T, YB + .1, -0.07, -0.02, M["tile"], C_BAL)
box("BalconySoffit", -OX, OX, YW + T, YB + .1, OH + .02, OH + .12, M["soffit"], C_BAL)
box("BalconySideL", -OX - .25, -OX, YW + T, YB, -0.07, OH + .12, M["granite"], C_BAL)
box("BalconySideR", OX, OX + .25, YW + T, YB, -0.07, OH + .12, M["granite"], C_BAL)
RH = 1.0
for i in range(5):
    x = -OX + .05 + i * (2 * OX - .1) / 4
    box(f"RailPost{i}", x - .025, x + .025, YB - .025, YB + .025, 0, RH, M["steel"], C_BAL)
box("RailTop", -OX, OX, YB - .03, YB + .03, RH - .03, RH + .02, M["steel"], C_BAL)
box("RailGlass", -OX + .05, OX - .05, YB - .006, YB + .006, .05, RH - .05, M["glass"], C_BAL)
box("RailBase", -OX, OX, YB - .1, YB + .1, -0.02, .06, M["steel"], C_BAL)

# ---------------------------------------------------------------- exterior view (image) + daylight
def script_dirs():
    cands = []
    try: cands.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError: pass
    for t in bpy.data.texts:
        if t.filepath: cands.append(os.path.dirname(bpy.path.abspath(t.filepath)))
    if bpy.data.filepath: cands.append(os.path.dirname(bpy.data.filepath))
    return [d for d in cands if d and os.path.isdir(d)]

def find_asset(fname):
    for d in script_dirs():
        p = os.path.join(d, fname)
        if os.path.exists(p): return p
    return None

if WITH_VIEW:
    D = 45.0
    px = D / 1445.0                       # metres per photo pixel at distance D (1500-px-wide photo space)
    vw, vh = (804 + 520) * px, 420 * px
    vx = ((356 + 1160) / 2 - 750) * px
    vz = EYE + (1000 - (850 + 1270) / 2) * px
    me = bpy.data.meshes.new("ViewBackdrop"); bm = bmesh.new()
    vs = [bm.verts.new((vx + sx * vw / 2, YW + D, vz + sz * vh / 2)) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    f = bm.faces.new(vs); uv = bm.loops.layers.uv.new("UVMap")
    for loop, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): loop[uv].uv = (u, v)
    bm.to_mesh(me); bm.free()
    mv = bpy.data.materials.new("ViewImage"); mv.use_nodes = True; nt = mv.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.6
    img_path = find_asset("trees.jpg")
    if img_path:
        it = nt.nodes.new("ShaderNodeTexImage"); it.image = bpy.data.images.load(img_path)
        nt.links.new(it.outputs["Color"], em.inputs["Color"])
    else:
        print("trees.jpg not found next to the script - using a flat sky colour")
        em.inputs["Color"].default_value = (0.6, 0.8, 0.95, 1)
    nt.links.new(em.outputs["Emission"], nt.nodes["Material Output"].inputs["Surface"])
    me.materials.append(mv); ob = bpy.data.objects.new("ViewBackdrop", me); C_EXT.objects.link(ob)

# soft daylight through the window
ld = bpy.data.lights.new("WindowDaylight", 'AREA'); ld.shape = 'RECTANGLE'; ld.size = 2 * OX; ld.size_y = OH
ld.energy = 900; ld.color = (0.93, 0.97, 1.0)
lo = bpy.data.objects.new("WindowDaylight", ld); lo.location = (0, YW + .4, OH / 2)
lo.rotation_euler = (math.radians(-90), 0, 0); C_LIGHT.objects.link(lo)

# world: bright sky
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World"); scene.world = world; world.use_nodes = True
wn = world.node_tree.nodes; wbg = wn.get("Background") or wn.new("ShaderNodeBackground")
sky = wn.new("ShaderNodeTexSky"); sky.sky_type = 'NISHITA'; sky.sun_elevation = math.radians(40); sky.sun_rotation = math.radians(160)
world.node_tree.links.new(sky.outputs["Color"], wbg.inputs["Color"]); wbg.inputs["Strength"].default_value = 0.25
world.node_tree.links.new(wbg.outputs["Background"], wn["World Output"].inputs["Surface"])

# ---------------------------------------------------------------- cameras
def camera(name, res, lens, sensor_fit, target_z):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 36; cd.sensor_fit = sensor_fit
    co = bpy.data.objects.new(name, cd); scene.collection.objects.link(co)
    co.location = (0, 0, EYE)
    co.rotation_euler = (math.radians(90) + math.atan2(target_z - EYE, YW), 0, 0)
    return co
cam_photo = camera("Cam_Photo", (1536, 2048), 18 * 1445 / 750, 'HORIZONTAL', EYE)   # same view as the photo (portrait)
cam_web = camera("Cam_Web16x9", (1920, 1080), 30, 'HORIZONTAL', EYE + 0.5)          # landscape hero
scene.camera = cam_photo
scene.render.resolution_x, scene.render.resolution_y = 1536, 2048

# ---------------------------------------------------------------- render settings
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = 0.3

# pack the image into the .blend and save next to the script if possible
try: bpy.ops.file.pack_all()
except Exception as e: print("pack_all skipped:", e)
dirs = script_dirs(); out_dir = dirs[0] if dirs else None
if out_dir and not bpy.data.filepath:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, "naus_living.blend"))
print("NAUS living room built.")
