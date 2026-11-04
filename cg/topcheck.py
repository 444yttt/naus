import bpy, math
from mathutils import Vector
__file__ = '/home/user/naus/cg/composite.py'
exec(open(__file__).read().split("if refl_mode:")[0])
for o in list(sc.objects):
    if o.type == 'MESH' and o.name.split('.')[0] in ('ceiling', 'wall_right', 'wall_top', 'pier', 'w1_head', 'w2_head', 'w1_sill', 'w2_sill'): o.hide_render = True
    if o.type == 'MESH': o.is_shadow_catcher = False; o.visible_camera = True
sc.render.film_transparent = False; sc.cycles.samples = 8
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0; sun.data.energy = 2
co.data.type = 'ORTHO'; co.data.ortho_scale = 3.2; co.data.shift_x = co.data.shift_y = 0
co.matrix_world = __import__('mathutils').Matrix.Translation((-3.4, -0.75, 5)) @ __import__('mathutils').Euler((0, 0, math.radians(180)), 'XYZ').to_matrix().to_4x4()
sc.render.resolution_x = sc.render.resolution_y = 800; sc.render.image_settings.file_format = 'PNG'
sc.render.filepath = S + 'comp/topcheck.png'; bpy.ops.render.render(write_still=True)
