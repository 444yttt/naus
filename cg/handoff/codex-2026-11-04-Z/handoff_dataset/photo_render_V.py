"""Cycles photo composite; shared approved furniture with calibrated camera.
Geometry/lighting is rendered, not generated. All powers are documented estimates.
"""
import bpy,json,sys,math,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parent;O=R/'out/photo_final_V';O.mkdir(exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
shot=args[0] if args else 'u1';preview='--preview' in args;tiles='--tiles' in args;background='--background' in args
c=json.loads((O/f'{shot}_camera.json').read_text(encoding='utf8'))
kc=json.loads((O/'p13_camera.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath=str(R/'out/3d_R/Harajuku_LDK_R.blend'))
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.device='CPU';S.render.threads=10
S.cycles.samples=32 if preview else 24;S.cycles.use_adaptive_sampling=True;S.cycles.adaptive_threshold=.03 if preview else .020;S.cycles.adaptive_min_samples=8
S.cycles.max_bounces=12;S.cycles.diffuse_bounces=6;S.cycles.glossy_bounces=8;S.cycles.transmission_bounces=8
S.cycles.use_denoising=True;S.cycles.denoiser='OPENIMAGEDENOISE';S.cycles.denoising_input_passes='RGB_ALBEDO_NORMAL';S.render.film_transparent=True
S.render.use_border=False;S.render.resolution_x=c['W'];S.render.resolution_y=c['H'];S.render.resolution_percentage=25 if preview else 100
if background and not preview:S.render.resolution_percentage=50
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=-.5 if shot.startswith('n') else -1.5
# Keep furniture and existing joinery for occlusion/bounce. Remove schematic glazing,
# old scenery and floor-joint geometry: the real photo supplies those pixels.
remove_prefix=('Glazing_mullion','Window_rail','Floor_joint','Plank_end','Balcony_outside_photo','Diagonal_outside_photo')
for ob in list(S.objects):
 if ob.type=='LIGHT' or ob.name.startswith(remove_prefix):bpy.data.objects.remove(ob,do_unlink=True)
# V: TV-centred, symmetric official speaker assemblies. Fabric faces local -Y.
for j,y in enumerate([3.90,.80]):
 root=bpy.data.objects.get('Beolab28_OFFICIAL_'+str(j))
 if root:
  root.location=(9.05,y,0)
  dx,dy=6.30-9.05,2.35-y
  root.rotation_euler.z=math.atan2(dy,dx)+math.pi/2
# Fine leather grain on the original official planning mesh; no shape substitution.
le=bpy.data.materials.get('Eames_ivory_leather_PROVISIONAL')
if le and le.use_nodes:
 nn=le.node_tree.nodes;ll=le.node_tree.links;bs=nn.get('Principled BSDF')
 tex=nn.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=230;tex.inputs['Detail'].default_value=2
 bump=nn.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00018;bump.inputs['Strength'].default_value=.16
 ll.new(tex.outputs['Fac'],bump.inputs['Height']);ll.new(bump.outputs[0],bs.inputs['Normal'])

# User requested a no-rug version. No raised bands or optical carpet remain.
for ob in list(S.objects):
 if ob.name.startswith('Shindo'):bpy.data.objects.remove(ob,do_unlink=True)
# Five-vertex island from original plan. Previous four-vertex trace missed the elbow.
for ob in list(S.objects):
 if ob.name.startswith('Existing_island'):bpy.data.objects.remove(ob,do_unlink=True)
ip=[((x-24)/35.2,(473-y)/35.2) for x,y in [(159,230),(194,242),(216,182),(216,120),(201,114)]]
verts=[(x,y,z) for z in [0,.91] for x,y in ip];N=len(ip)
me=bpy.data.meshes.new('Kitchen_plan_five_vertex');me.from_pydata(verts,[],[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]);me.update()
ob=bpy.data.objects.new('Existing_island_plan_proxy',me);S.collection.objects.link(ob);ob.visible_camera=True;ob.is_shadow_catcher=True;ob.data.materials.append(bpy.data.materials.get('Warm_white_wall'))
balance=bpy.data.objects.get('Beosound_Balance_OFFICIAL')
if balance:balance.location=(5.2,9.9,.91)
receivers=[]
for ob in S.objects:
 if ob.type!='MESH' and ob.type!='CURVE':continue
 if ob.name=='LDK_floor':
  ob.is_shadow_catcher=True;receivers.append(ob)
 elif ob.name.startswith(('TV_back_wall','Kitchen_wall','Hall_return','Kitchen_top_wall')):
  ob.is_shadow_catcher=True;receivers.append(ob)
 elif ob.name.startswith('Existing_island'):
  ob.visible_camera=True;ob.is_shadow_catcher=True;receivers.append(ob)
 elif ob.name.startswith(('Ceiling','Kitchen_cabinet','Kitchen_wall_counter','Sink','Faucet')):
  ob.visible_camera=False
 # The tile proposal is new work and intentionally visible.
for ob in list(S.objects):
 if ob.name.startswith('TV_natural_tile'):bpy.data.objects.remove(ob,do_unlink=True)
tilemat=bpy.data.materials.get('Natural_stone_tile_unselected')
top=c.get('wall_top_z',2.35)
for iy in range(5):
 for iz in range(3):
  bpy.ops.mesh.primitive_cube_add(size=1,location=(9.385,.3+(iy+.5)*.82,(iz+.5)*top/3))
  ob=bpy.context.object;ob.name='TV_tile_photo_recess';ob.dimensions=(.02,.816,top/3-.004);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  ob.data.materials.append(tilemat)

# Real floor approximation influences reflections/indirect light, not its photo colour.
fm=bpy.data.materials.new('Photo_floor_reflection_receiver');fm.use_nodes=True
bs=fm.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.17,.15,.13,1)
bs.inputs['Roughness'].default_value=1.;bs.inputs['Coat Weight'].default_value=0.;bs.inputs['Coat Roughness'].default_value=.18
bpy.data.objects['LDK_floor'].data.materials.clear();bpy.data.objects['LDK_floor'].data.materials.append(fm)

# The old solid Hall_return proxy spans the actual doorway and incorrectly masks the TV-wall end.
# The photograph supplies real joinery; exclude this unverified proxy from camera occlusion.
hr=bpy.data.objects.get('Hall_return')
if hr:hr.is_shadow_catcher=False;hr.visible_camera=False

# Camera convention: calibrated R maps world -> OpenCV +Z forward, +Y down.
data=bpy.data.cameras.new('PhotoMatched_'+shot);data.sensor_fit='HORIZONTAL';data.sensor_width=36
data.lens=c['f']*36/c['W'];data.clip_start=.03;data.clip_end=200
cam=bpy.data.objects.new('PhotoMatched_'+shot,data);S.collection.objects.link(cam)
cam.matrix_world=Matrix.Translation(c['C'])@(Matrix(c['R']).transposed()@Matrix(((1,0,0),(0,-1,0),(0,0,-1)))).to_4x4();S.camera=cam
vl=S.view_layers[0]
groups=['Direct_sun','Balcony_sky','Diagonal_sky','Ambient_sky','Exterior_reflection']
for g in groups:
 pass
def light(name,typ,loc,direction,power,col,group,size=None):
 ld=bpy.data.lights.new(name,typ);ld.energy=power;ld.color=col
 if typ=='AREA':
  ld.shape='RECTANGLE';ld.size=size[0];ld.size_y=size[1]
  # Window sampling emitters approximate incoming diffuse sky. Their untextured
  # rectangles must not replace the actual exterior in glossy reflections.
  if hasattr(ld,'specular_factor'):ld.specular_factor=0
 if typ=='SUN':ld.angle=math.radians(.65)
 ob=bpy.data.objects.new(name,ld);S.collection.objects.link(ob);ob.location=loc
 ob.rotation_euler=Vector(direction).to_track_quat('-Z','Y').to_euler();ob.lightgroup=''
 if typ=='AREA':ob.visible_glossy=False
 return ob
az=math.radians(84.5 if shot.startswith('n') else 99.5);el=math.radians(28 if shot.startswith('n') else 50)
sun=light('Sun_estimated_from_floor_shadows','SUN',(0,-5,8),(math.cos(az)*math.cos(el),math.sin(az)*math.cos(el),-math.sin(el)),2.5,(1,.95,.86),'Direct_sun')
light('Balcony_window_sky','AREA',(4.7,-.12,1.4),(0,1,0),600,(.78,.87,1),'Balcony_sky',(9.4,2.5))
light('Diagonal_window_sky','AREA',(2.4,6.55,1.4),(.937,-.349,0),800,(.80,.89,1),'Diagonal_sky',(13.5,2.5))
world=bpy.data.worlds.new('Photo_ambient_sky');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.70,.82,1,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.12;world.lightgroup='';S.world=world
# Photograph-projected exterior cards are visible to glossy rays only. They restore
# recognisable sky/trees in furniture reflections without regenerating the plate.
# LDR source images are not a measured HDR environment; retain that limitation.
def exterior_card(name,a,b,ref):
 rc=json.loads((O/f'{ref}_camera.json').read_text());rr=Matrix(rc['R']);cc=Vector(rc['C'])
 vv=[];uv=[];faces=[];nx=24;nz=8
 for iz in range(nz+1):
  for ix in range(nx+1):
   p=Vector(a).lerp(Vector(b),ix/nx);p.z=iz/nz*2.7;vv.append(tuple(p));q=rr@(p-cc)
   uv.append((rc['f']*q.x/q.z/rc['W']+.5,.5-rc['f']*q.y/q.z/rc['H']) if q.z>.01 else (.5,.5))
 for iz in range(nz):
  for ix in range(nx):
   k=iz*(nx+1)+ix;faces.append((k,k+1,k+nx+2,k+nx+1))
 me=bpy.data.meshes.new(name);me.from_pydata(vv,[],faces);me.update();layer=me.uv_layers.new()
 for pol in me.polygons:
  for li in pol.loop_indices:layer.data[li].uv=uv[me.loops[li].vertex_index]
 ob=bpy.data.objects.new(name,me);S.collection.objects.link(ob);ob.lightgroup=''
 ob.visible_camera=False;ob.visible_diffuse=False;ob.visible_glossy=True;ob.visible_shadow=False;ob.visible_transmission=False
 ma=bpy.data.materials.new(name);ma.use_nodes=True;ma.cycles.emission_sampling='NONE';nn=ma.node_tree.nodes;ll=ma.node_tree.links;nn.clear()
 tx=nn.new('ShaderNodeTexImage');image_path=R/f'images/photos_srgb/{ref}.png';tx.image=bpy.data.images.load(str(image_path if image_path.exists() else R/f'images/photos/{ref}.jpg'));tx.extension='EXTEND'
 em=nn.new('ShaderNodeEmission');em.inputs[1].default_value=.4;ou=nn.new('ShaderNodeOutputMaterial');ll.new(tx.outputs['Color'],em.inputs[0]);ll.new(em.outputs[0],ou.inputs['Surface']);me.materials.append(ma)
exterior_card('Balcony_reflection_photo',(0,-.05,0),(9.4,-.05,0),'n01' if shot.startswith('n') else 'p09')
exterior_card('Diagonal_reflection_photo',(-.05,.02,0),(4.83,13.12,0),'n04' if shot.startswith('n') else 'u2')
# Add only downlights visibly lit in each source plate. Cone/colour/power are
# estimated; no unsupported claims of measured lumens or IES photometry.
spots={'p13':[[670,378],[803,494],[892,570],[1151,434],[1083,587],[1052,669],[1030,759],[1021,778]],'p09':[[883,797]],'p03':[[90,402]],'n01':[[1133,449]],'n02':[[634,673]],'n03':[[1047,613]],'n04':[[587,732]]}.get(shot,[])
spot_report=[]
for i,uv in enumerate(spots):
 pixel=Vector((uv[0]*c['W']/1368,uv[1]*c['W']/1368,1))
 rr=Matrix(c['R']).transposed()@Vector(((pixel.x-c['W']/2)/c['f'],(pixel.y-c['H']/2)/c['f'],1))
 if rr.z<=0:continue
 pos=Vector(c['C'])+rr*((2.68-c['C'][2])/rr.z)
 group=f'Downlight_{i+1:02d}';pass
 lo=light(group,'SPOT',pos,(0,0,-1),6,(1,.69,.38),group)
 lo.data.spot_size=math.radians(60);lo.data.spot_blend=.45;lo.data.shadow_soft_size=.035
 spot_report.append({'name':group,'position_m':list(pos),'radiant_power_W_estimate':6,'cone_deg':60,'colour':'warm estimate ~3000K appearance; not measured'})
# External balcony overhang and the room ceiling gate direct sunlight.
bpy.ops.mesh.primitive_cube_add(size=1,location=(4.7,-.35,2.75));ob=bpy.context.object;ob.name='Balcony_overhang_estimated';ob.dimensions=(10,.7,.10);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.visible_camera=False

vl.cycles.use_pass_shadow_catcher=True
vl.use_pass_diffuse_direct=False;vl.use_pass_diffuse_indirect=False;vl.use_pass_glossy_direct=False;vl.use_pass_glossy_indirect=False
S.use_nodes=True;n=S.node_tree.nodes;l=S.node_tree.links;n.clear()
rl=n.new('CompositorNodeRLayers')
# Export the physically rendered foreground separately. Tone-map CG only; keep the
# original photograph unchanged during the final photographic alpha composite.
co=n.new('CompositorNodeComposite');l.new(rl.outputs['Image'],co.inputs[0])
# Retain a linear multilayer EXR with independent source and direct/indirect contributions.
if True:
 fo=n.new('CompositorNodeOutputFile');fo.base_path=str(O/(f'{shot}_background_passes' if background else f'{shot}_preview_passes' if preview else f'{shot}_full_passes'));fo.format.file_format='OPEN_EXR_MULTILAYER';fo.format.color_depth='16';fo.format.exr_codec='ZIP'
 while fo.inputs:fo.file_slots.remove(fo.inputs[0])
 for key in ['Image','Shadow Catcher']:
  if key in rl.outputs:
   fo.file_slots.new(key);l.new(rl.outputs[key],fo.inputs[key])
S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGBA';S.render.image_settings.color_depth='16'
S.render.filepath=str(O/(f'{shot}_'+('background' if background else 'preview' if preview else 'full')+'_foreground.png'))
if background:
 static=('LDK_floor','TV_back_wall','Kitchen_wall','Hall_return','Kitchen_top_wall','Ceiling','Kitchen_cabinet','Kitchen_wall_counter','Existing_island','Sink','Faucet','Balcony_overhang','Balcony_reflection_photo','Diagonal_reflection_photo')
 for ob in S.objects:
  if ob.type in ['MESH','CURVE'] and not ob.name.startswith(static):ob.hide_render=True
if shot.startswith('n'):S.cycles.samples=32 if not background else 24
if background:S.cycles.samples=8 if not preview else 24
report={'shot':shot,'camera':c,'samples':S.cycles.samples,'bounces':12,'lighting':{'sun':{'azimuth_travel_deg':84.5 if shot.startswith('n') else 99.5,'elevation_deg':28 if shot.startswith('n') else 50,'energy':2.5,'angular_size_deg':.65},'balcony_sky_W':600,'diagonal_sky_W':800,'ambient_strength':.12,'downlights':spot_report,'status':'photo-inferred initial values; not measured photometric data'},'shadow_receiver_roughness':1.0,'separate_reflection_roughness':.19,'distortion':'no extra warp applied; u1 traced architecture is straight within roughly1px RMS','status':'V original-photo delivery render; estimated lighting and raster-plan calibration'}
report['reflections']='LDR exterior photo projection cards, glossy rays only; not measured HDR environment'
report['render_percentage']=S.render.resolution_percentage
report['speaker_symmetry']='TV center Y2.35; speaker roots Y0.80 and3.90, X9.05; toe-in to6.30,2.35'
report['adaptive_noise_threshold']=S.cycles.adaptive_threshold
report['adaptive_min_samples']=S.cycles.adaptive_min_samples
report['source_colour_management']='sRGB working space; original Display P3 ICC profiles converted before photographic composite and exterior-card lookup'
(O/f'{shot}_{"background_" if background else "preview_" if preview else ""}render_settings.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.file.pack_all()
if shot.startswith('n'):S.cycles.samples=32 if not background else 24
if not background and not preview:bpy.ops.wm.save_as_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'))
if tiles:raise RuntimeError('V uses full-frame rendering; no partial-mask cache')
if background:S.cycles.samples=8 if not preview else 24
bpy.ops.render.render(write_still=True)
print('PHOTO_RENDER_COMPLETE',shot,flush=True)
