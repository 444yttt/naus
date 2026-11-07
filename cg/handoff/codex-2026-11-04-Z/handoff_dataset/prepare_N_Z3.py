"""Z3 new views n03/n04 (user-supplied 1086x1448 photos, taken at a different time of day).
Scene = Z2 common scene (identical furniture/layout/materials/rug) + camera for the photo +
the sun of THAT photo measured from its floor shadows + shadow-only window frame derived from
the photographed mullion shadows. The five original views keep their own sun; nothing common changes."""
from pathlib import Path
import bpy,json,sys,math
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parent;O=R/'out_Z3';args=sys.argv[sys.argv.index('--')+1:];shot=args[0]
P=json.loads((O/'n_view_params.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/'out_Z2/u1_photo_scene.blend'));S=bpy.context.scene
c=json.loads((O/f'{shot}_camera_Z3.json').read_text());cam=S.camera
cam.matrix_world=Matrix.Translation(c['C'])@(Matrix(c['R']).transposed()@Matrix(((1,0,0),(0,-1,0),(0,0,-1)))).to_4x4()
cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=36;cam.data.lens=c['f']*36/c['W'];cx,cy=c['principal_point_native_px']
cam.data.shift_x=-(cx-c['W']/2)/c['W'];cam.data.shift_y=(cy-c['H']/2)/c['W']
S.render.resolution_x=c['W'];S.render.resolution_y=c['H'];S.render.resolution_percentage=100;S.render.use_border=False
sun=S.objects['Sun_estimated_from_floor_shadows'];d=Vector(P['sun_toward_by_shot'][shot])
sun.rotation_euler=d.to_track_quat('Z','Y').to_euler();sun.data.energy=P['sun_strength'];sun.data.angle=math.radians(.53)
g=P['light_gain_rgb_by_shot'][shot]
for o in S.objects:
    if o.type=='LIGHT':o.data.color=tuple(min(ch*gg,10) for ch,gg in zip(o.data.color,g))
bg=S.world.node_tree.nodes['Background'];col=bg.inputs['Color'].default_value;bg.inputs['Color'].default_value=(col[0]*g[0],col[1]*g[1],col[2]*g[2],1)
S.view_settings.exposure=P['exposure_by_shot'][shot]
# shadow-only window frame (not seen by camera, glossy or transmission rays)
def box(name,x0,x1,y0,y1,z0,z1):
    me=bpy.data.meshes.new(name);vs=[(x,y,z) for x in (x0,x1) for y in (y0,y1) for z in (z0,z1)]
    fs=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)];me.from_pydata(vs,[],fs);ob=bpy.data.objects.new(name,me);S.collection.objects.link(ob)
    ob.visible_camera=False;ob.visible_glossy=False;ob.visible_transmission=False;ob.visible_diffuse=True;ob.visible_shadow=True
    ma=bpy.data.materials.get('Window_frame_shadow_Z3') or bpy.data.materials.new('Window_frame_shadow_Z3');ma.use_nodes=True;ma.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.02,.02,.02,1);me.materials.append(ma);return ob
for i,(x,wd) in enumerate(zip(P['mullion_x'],P['mullion_width'])):box(f'Window_frame_shadow_Z3_mullion{i}',x-wd/2,x+wd/2,-.06,0,0,2.486)
for i,(a,b) in enumerate(P['solid_wall_spans_x']):box(f'Window_frame_shadow_Z3_wall{i}',a,b,-.2,0,0,2.7)
for i,x in enumerate(P['glazing_ends_x']):box(f'Window_frame_shadow_Z3_jamb{i}',x-.06,x+.06,-.1,0,0,2.7)
box('Window_frame_shadow_Z3_head',0,9.4,-.08,0,2.486,2.7)
box('Window_frame_shadow_Z3_handrail',0,9.4,P['handrail_y']-.03,P['handrail_y']+.03,P['handrail_z']-.03,P['handrail_z']+.03)
for nd in S.node_tree.nodes:
    if nd.type=='OUTPUT_FILE':nd.base_path=str(O/f'{shot}_full_passes')
S.render.filepath=str(O/f'{shot}_full_foreground.png')
(O/f'{shot}_camera.json').write_text(json.dumps(c,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));print('Z3_N_PREPARED',shot,flush=True)
