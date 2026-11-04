"""Render the furniture of a layout option into a calibrated photo (Blender, Cycles).

blender -b -P composite.py -- <view> <option> <mode> <scale> <samples> <out_prefix> [light.json]
mode: sun | amb  -> lighting-calibration renders of the empty room (sun only / sky only)
      final      -> furniture with shadow-catcher room, using the fitted light.json
      refl       -> the whole scene mirrored below the floor (furniture only visible): the polished tile's reflection

Room geometry (metres, floor frame of layout.json) was measured from the calibrated photos: window glass from
z 0.07 to 2.40, mullions every 1.17 m, pier between the two window walls. The room surfaces are shadow catchers,
so only what the furniture adds (its own pixels, shadows, occlusion) is composited over the photo."""
import bpy, sys, json, math, os
from mathutils import Matrix, Vector
A = sys.argv[sys.argv.index('--') + 1:]
view, opt, mode, scale, spp, out = A[0], A[1], A[2], float(A[3]), int(A[4]), A[5]
light = json.load(open(A[6])) if len(A) > 6 else None
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import furniture
S = '/tmp/claude-0/-home-user-naus/93a99187-9df5-51d5-b3db-c42aa0696673/scratchpad/'
L = json.load(open(os.path.join(HERE, 'layout.json'))); cams = json.load(open(S + 't2/cams.json'))
calib = json.load(open(S + 't2/%s_calib.json' % view))
SUN = dict(az_dir=(0.4695, -0.8829), el=25.5)    # direction the light travels (floor frame), elevation in degrees;
                                                     # fitted to the sunlit stripes on the floor in photos 1 and 2 (sunfit.py)
HEAD, SILL, CEIL = 2.40, 0.07, 2.65

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.cycles.samples = spp; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 6
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
sc.render.resolution_x, sc.render.resolution_y = int(1932 * scale), int(2576 * scale)
sc.render.film_transparent = True; sc.cycles.film_transparent_glass = True   # the photo shows through glass tops
sc.render.image_settings.file_format = 'OPEN_EXR'; sc.render.image_settings.color_depth = '32'
sc.render.image_settings.exr_codec = 'ZIP'

# camera: OpenCV Rcw (world->camera, y down, z forward) -> Blender (y up, looking down -z)
K = calib['K']; R = Matrix(calib['Rcw']); C = Vector((*cams[view]['cam'], cams[view]['h']))
cam = bpy.data.cameras.new('cam'); co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
cam.sensor_fit = 'HORIZONTAL'; cam.sensor_width = 36; cam.lens = K[0][0] * 36 / 1932
cam.shift_x = -(K[0][2] - 966) / 1932; cam.shift_y = (K[1][2] - 1288) / 1932
cam.clip_start = 0.05
co.matrix_world = Matrix.Translation(C) @ (R.transposed() @ Matrix.Diagonal((1, -1, -1))).to_4x4()

def mat(name, rgb, rough=0.6):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough; return m
calib_mode = mode in ('sun', 'amb'); refl_mode = mode == 'refl'
FLOOR_ALB = (0.66, 0.62, 0.53)                      # cream tile (luminance ~0.62); calibration renders use it too
floor_alb = FLOOR_ALB
M_floor = mat('floor', floor_alb, 0.35 if calib_mode else 0.12)    # polished tile: catches the furniture's reflections in the final pass
if not calib_mode: M_floor.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value = 0.6; M_floor.node_tree.nodes['Principled BSDF'].inputs['Coat Roughness'].default_value = 0.04
M_wall = mat('wall', (0.72, 0.69, 0.63)); M_ceil = mat('ceil', (0.8, 0.79, 0.76))
M_frame = mat('frame', (0.03, 0.03, 0.03), 0.4)
def box(name, x0, x1, y0, y1, z0, z1, m, camera=True, catcher=False):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object; o.name = name; o.scale = (x1 - x0, y1 - y0, z1 - z0); bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m); o.visible_camera = camera and not refl_mode; o.is_shadow_catcher = (catcher or not calib_mode) and not refl_mode; return o
XR, XW, YT, YW = -4.69, 0.89, -4.83, 0.87          # right wall, W2 glass, top wall, W1 glass
t = 0.2
catch = not calib_mode
fl = box('floor', XR, XW, YT, YW, -0.1, 0, M_floor, True, catch)
box('ceiling', XR, XW, YT, YW, CEIL, CEIL + t, M_ceil, False)          # must stop at the glass: outside is open sky
box('wall_right', XR - t, XR, YT, YW, 0, CEIL, M_wall, catch, catch)
box('wall_top', XR, XW, YT - t, YT, 0, CEIL, M_wall, False)
box('pier', 0, XW, 0, YW, 0, CEIL, M_wall, False)
for (a0, a1) in ((XR, 0), ):                         # W1 wall (y = YW): sill and soffit strips, mullions
    box('w1_sill', a0, a1, YW - t, YW, 0, SILL, M_wall, False); box('w1_head', a0, a1, YW - t, YW, HEAD, CEIL, M_wall, False)
box('w2_sill', XW - t, XW, YT, 0, 0, SILL, M_wall, False); box('w2_head', XW - t, XW, YT, 0, HEAD, CEIL, M_wall, False)
for x in (-1.18, -2.355, -3.53): box('w1_mullion', x - 0.025, x + 0.025, YW, YW + 0.12, SILL, HEAD, M_frame, False)
for y in (-1.18, -2.355, -3.53): box('w2_mullion', XW, XW + 0.12, y - 0.025, y + 0.025, SILL, HEAD, M_frame, False)
box('w1_endpost', XR - 0.05, XR + 0.03, YW, YW + 0.12, SILL, HEAD, M_frame, False)
box('w2_endpost', XW, XW + 0.12, YT - 0.05, YT + 0.03, SILL, HEAD, M_frame, False)
# sky enters only through the two window openings; portals help Cycles find it
for nm, loc, rot, size in (('portal_w1', ((XR + 0) / 2, YW + 0.15, (SILL + HEAD) / 2), (math.radians(-90), 0, 0), (abs(XR), HEAD - SILL)),
                           ('portal_w2', (XW + 0.15, (YT + 0) / 2, (SILL + HEAD) / 2), (0, math.radians(90), 0), (HEAD - SILL, abs(YT)))):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot); p = bpy.context.object; p.data.shape = 'RECTANGLE'
    p.data.size, p.data.size_y = size; p.data.cycles.is_portal = True
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']
bpy.ops.object.light_add(type='SUN'); sun = bpy.context.object; sun.data.angle = math.radians(0.53)
d = Vector((SUN['az_dir'][0] * math.cos(math.radians(SUN['el'])), SUN['az_dir'][1] * math.cos(math.radians(SUN['el'])), -math.sin(math.radians(SUN['el']))))
sun.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
if mode == 'sun': sun.data.energy = 1.0; bg.inputs['Strength'].default_value = 0.0
elif mode == 'amb': sun.data.energy = 0.0; bg.inputs['Color'].default_value = (1, 1, 1, 1); bg.inputs['Strength'].default_value = 1.0
else:
    s = light['sun']; a = light['sky']
    sun.data.color = [c / max(s) for c in s]; sun.data.energy = max(s)
    bg.inputs['Color'].default_value = (*[c / max(a) for c in a], 1); bg.inputs['Strength'].default_value = max(a)

if not calib_mode:
    items = L['options'][opt]['items']
    ON = {'dining_table': 0.733, 'plinth_tall': 0.51}
    def place(key, it, z=0.0):
        ob, dim = furniture.LIBRARY[key](S + 'models')
        ob.rotation_mode = 'XYZ'                       # glTF/USD imports come in quaternion mode
        ob.location = (it['x'], it['y'], z); ob.rotation_euler = (0, 0, math.radians(it.get('rot', 0))); return ob
    for it in items:
        k = it.get('model')
        if not k or k not in furniture.LIBRARY: continue
        if it['type'] == 'homeview': continue            # on the kitchen counter, outside photos 1 and 2
        z = 0.0
        if it.get('on') == 'dining_table': z = ON['dining_table']
        if it['type'] == 'smart_speaker': z = ON['plinth_tall']
        if it['type'] == 'tv': z = 0.55                   # wall mount, bottom edge 55 cm above the floor
        z = it.get('z', z)                                # explicit height (things standing on other things)
        place(k, it, z)
if refl_mode:
    # mirror everything (room, lights, furniture) through the floor plane; seen from the real camera this is the image
    # a perfect mirror floor would show
    flip = bpy.data.objects.new('mirror', None); sc.collection.objects.link(flip); flip.scale = (1, 1, -1)
    for o in list(sc.objects):
        if o not in (flip, co) and o.parent is None: o.parent = flip
if not calib_mode and not refl_mode:
    vl = sc.view_layers[0]; vl.cycles.use_pass_shadow_catcher = True
    # write the objects (Combined, premultiplied RGBA) and the shadow-catcher factor as separate EXRs
    sc.use_nodes = True; nt = sc.node_tree; rl = nt.nodes['Render Layers']
    fo = nt.nodes.new('CompositorNodeOutputFile'); fo.base_path = os.path.dirname(out); fo.format.file_format = 'OPEN_EXR'
    fo.format.color_depth = '32'; fo.file_slots.clear()
    for name, sock in (('combined', 'Image'), ('catcher', 'Shadow Catcher')):
        fo.file_slots.new(os.path.basename(out) + '_' + name + '_'); nt.links.new(rl.outputs[sock], fo.inputs[-1])
sc.render.filepath = out; bpy.ops.render.render(write_still=True)
