"""Refine the existing physical scene; preserve camera and common furniture transforms."""
from pathlib import Path
import bpy,bmesh,sys,json,math
R=Path(__file__).resolve().parent; V=R/'out/photo_final_V'; O=R/'out/photo_final_W';O.mkdir(exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:];shot=args[0];preview='--preview' in args;prepare='--prepare' in args;background='--background' in args
bpy.ops.wm.open_mainfile(filepath=str(V/f'{shot}_photo_scene.blend'));S=bpy.context.scene
# Smooth only the low resolution curved plywood shells and upholstery. Do not
# subdivide the star base/glides, or move the contact geometry.
mesh_report=[]
for ob in S.objects:
 if ob.type!='MESH':continue
 if ob.name.startswith(('SEAT-OUTER_SHELL','SEAT-FABRIC')):
  ob.data=ob.data.copy();bm=bmesh.new();bm.from_mesh(ob.data)
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
  bmesh.ops.join_triangles(bm,faces=list(bm.faces),angle_face_threshold=math.radians(35),angle_shape_threshold=math.radians(45),cmp_uvs=False,cmp_materials=True)
  # Crease sharp seams while allowing the broad shell silhouette to become curved.
  cre=bm.edges.layers.float.new('crease_edge')
  for e in bm.edges:
   if e.is_manifold and e.calc_face_angle(0)>math.radians(65):e[cre]=.50
  bm.to_mesh(ob.data);bm.free();ob.data.update()
  su=ob.modifiers.new('Curved shell refinement','SUBSURF');su.levels=2;su.render_levels=2
  for p in ob.data.polygons:p.use_smooth=True
  mesh_report.append({'object':ob.name,'original_vertices':len(ob.data.vertices),'subdivision':2})
# The planning upholstery has open, overlapping triangulated patches. Close those
# shells before voxel union; voxelizing open pads would wrongly delete cushions.
for ob in S.objects:
 if ob.type=='MESH' and ob.name.startswith('SEAT-FABRIC'):
  ob.modifiers.clear();bm=bmesh.new();bm.from_mesh(ob.data)
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
  bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
  md=ob.modifiers.new('Close upholstery tessellation seams','REMESH');md.mode='VOXEL';md.voxel_size=.0035;md.use_smooth_shade=True
  sm=ob.modifiers.new('Finish repaired upholstery','SMOOTH');sm.factor=.55;sm.iterations=3
  for entry in mesh_report:
   if entry['object']==ob.name:
    entry.pop('subdivision',None);entry.update(repair='closed boundary loops, outward normals, voxel union, smooth',voxel_size_m=.0035,smooth_iterations=3)
# Surface detail uses true world scale coordinates. Ernest is fabric, Eames leather.
for name,scale,strength,distance in [('Shedir02_Burro_colour_study',1450,.22,.00026),('Torii_light_grey_fabric_code_pending',1900,.18,.00018)]:
 ma=bpy.data.materials.get(name)
 if not ma or not ma.use_nodes:continue
 nn=ma.node_tree.nodes;ll=ma.node_tree.links;bs=nn.get('Principled BSDF')
 if not bs:continue
 bs.inputs['Roughness'].default_value=.62;bs.inputs['Sheen Weight'].default_value=.18;bs.inputs['Sheen Roughness'].default_value=.55
 tex=nn.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=2
 bump=nn.new('ShaderNodeBump');bump.inputs['Distance'].default_value=distance;bump.inputs['Strength'].default_value=strength
 ll.new(tex.outputs['Fac'],bump.inputs['Height']);ll.new(bump.outputs[0],bs.inputs['Normal'])
 # Albedo texture variation is only +/- 2%; preserve the selected light colour.
 col=tuple(bs.inputs['Base Color'].default_value)
 ramp=nn.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=tuple(x*.96 for x in col[:3])+(1,);ramp.color_ramp.elements[1].color=col
 ll.new(tex.outputs['Fac'],ramp.inputs[0]);ll.new(ramp.outputs[0],bs.inputs['Base Color'])
# Separate the shell timber finish from the coffee tables; slightly more diffuse
# return prevents an almost black underside while keeping the dark wood selection.
wood=bpy.data.materials.get('Ernest_dark_wood_study')
if wood:
 ew=wood.copy();ew.name='Eames_dark_wood_refined';bs=ew.node_tree.nodes.get('Principled BSDF')
 if bs:bs.inputs['Roughness'].default_value=.34
 for ob in S.objects:
  if ob.name.startswith('SEAT-OUTER_SHELL'):
   for slot in ob.material_slots:slot.material=ew
# Directional sky is less uniform; warm broad floor bounce and cool upper sky.
# This is the same lighting in all five cameras; retain the source photo exposure.
for ob in S.objects:
 if ob.type=='LIGHT' and ob.name in ['Balcony_window_sky','Diagonal_window_sky']:
  ob.data.energy*=.82
ld=bpy.data.lights.new('Window_low_green_bounce_estimate','AREA');ld.energy=90;ld.color=(.80,1.0,.84);ld.shape='RECTANGLE';ld.size=8;ld.size_y=1.0;ld.specular_factor=0
ob=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(ob);ob.location=(4.7,-.11,.6)
from mathutils import Vector
ob.rotation_euler=Vector((0,1,.25)).to_track_quat('-Z','Y').to_euler();ob.visible_glossy=False
# No per-view composition changes or moving furniture to conceal clipping.
S.render.threads=10;S.render.use_border=False;S.render.resolution_percentage=25 if preview else 100
# Trace the complete projected bounds of every visible new object, plus a generous
# receiver margin. Keep the original full-size canvas; unchanged sky/ceiling are
# supplied by the photograph, never by a resized furniture render.
from bpy_extras.object_utils import world_to_camera_view
static=('LDK_floor','TV_back_wall','Kitchen_wall','Hall_return','Kitchen_top_wall','Ceiling','Kitchen_cabinet','Kitchen_wall_counter','Existing_island','Sink','Faucet','Balcony_overhang','Balcony_reflection_photo','Diagonal_reflection_photo')
ys=[]
for ob in S.objects:
 if ob.type in ['MESH','CURVE'] and not ob.hide_render and ob.visible_camera and not ob.name.startswith(static):
  for p in ob.bound_box:
   q=world_to_camera_view(S,S.camera,ob.matrix_world@Vector(p))
   if q.z>0:ys.append(q.y)
if ys:
 S.render.use_border=True;S.render.use_crop_to_border=False;S.render.border_min_x=0;S.render.border_max_x=1;S.render.border_min_y=0;S.render.border_max_y=min(1,max(ys)+.075)
# Verified opaque-alpha extents of the preceding full-frame native render, padded
# by 8% of image height. These also reject behind-camera bounding boxes crossing
# the near plane, whose projection is mathematically unbounded.
S.render.border_max_y={'u1':.68,'u2':.56,'p09':.54,'p01':.49,'p13':.57}[shot]
S.cycles.samples=32 if preview else 24;S.cycles.adaptive_threshold=.020;S.cycles.adaptive_min_samples=8
S.cycles.use_denoising=True;S.cycles.denoising_input_passes='RGB_ALBEDO_NORMAL'
S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGBA';S.render.image_settings.color_depth='16'
mode='preview' if preview else 'full'
S.render.filepath=str(O/f'{shot}_{mode}_foreground.png')
for n in S.node_tree.nodes:
 if n.type=='OUTPUT_FILE':n.base_path=str(O/f'{shot}_{mode}_passes')
if not preview and (not background or shot=='u2'):bpy.ops.wm.save_as_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'))
(O/f'{shot}_refinement.json').write_text(json.dumps({'mesh':mesh_report,'camera_and_layout':'unchanged from V','foreground_resolution_percent':S.render.resolution_percentage,'samples':S.cycles.samples,'source_photo':'original sRGB-converted plate; unchanged','furniture_materials':'fabric micro-bump / sheen, curved Eames shell, same light upholstery colours'},indent=2))
if background:
 hidden_before_background={ob.name:ob.hide_render for ob in S.objects}
 static=('LDK_floor','TV_back_wall','Kitchen_wall','Hall_return','Kitchen_top_wall','Ceiling','Kitchen_cabinet','Kitchen_wall_counter','Existing_island','Sink','Faucet','Balcony_overhang','Balcony_reflection_photo','Diagonal_reflection_photo')
 for ob in S.objects:
  if ob.type in ['MESH','CURVE'] and not ob.name.startswith(static):ob.hide_render=True
 S.cycles.samples=8;S.cycles.adaptive_min_samples=4;S.render.resolution_percentage=50
 S.render.filepath=str(O/f'{shot}_background_foreground.png')
 for n in S.node_tree.nodes:
  if n.type=='OUTPUT_FILE':n.base_path=str(O/f'{shot}_background_passes')
if not prepare:
 bpy.ops.render.render(write_still=True)
 # The first native u2 foreground began before the upholstery seam repair. Replace
 # its complete Eames ROI with a fresh native render, not a painted or scaled patch.
 if background and shot=='u2':
  for ob in S.objects:ob.hide_render=hidden_before_background[ob.name]
  S.render.resolution_percentage=100;S.render.use_border=True;S.render.use_crop_to_border=True
  x0,x1,y0,y1=0.10,.26,.28,.52
  S.render.border_min_x=x0;S.render.border_max_x=x1;S.render.border_min_y=y0;S.render.border_max_y=y1
  S.cycles.samples=32;S.cycles.adaptive_min_samples=8
  for node in list(S.node_tree.nodes):
   if node.type=='OUTPUT_FILE':S.node_tree.nodes.remove(node)
  S.render.filepath=str(O/'u2_repaired_native_ROI.png');bpy.ops.render.render(write_still=True)
  import subprocess
  subprocess.run(['C:/Users/akaay/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',str(R/'photo_patch_u2_W.py')],check=True)
 print('W_FOREGROUND_COMPLETE',shot,mode,flush=True)
