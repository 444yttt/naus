"""Local, editable 3D study driven by approved layout_M.json. No external uploads.
Official downloaded OBJ: Beolab28, Balance. Other shapes are documented study models.
"""
import bpy, math, json, sys, random
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent; O=R/'out'/'3d_M'; O.mkdir(exist_ok=True)
C=json.loads((R/'out/layout_M.json').read_text(encoding='utf-8-sig'))
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene; S.unit_settings.system='METRIC'; S.render.engine='CYCLES'
S.cycles.samples=24; S.cycles.use_denoising=True; S.cycles.max_bounces=6
S.render.resolution_x=1600; S.render.resolution_y=1100; S.render.resolution_percentage=100
S.view_settings.view_transform='AgX'; S.view_settings.look='AgX - Medium High Contrast'
S.view_settings.exposure=-.85
S.render.image_settings.file_format='PNG'; S.render.image_settings.color_mode='RGB'
S.render.threads_mode='FIXED';S.render.threads=10
manifest=[];arch=[]
def mat(name,col,rough=.5,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
def textured(name,c0,c1,kind='stone',rough=.5):
 m=mat(name,c0,rough);n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF');tc=n.new('ShaderNodeTexCoord');mp=n.new('ShaderNodeMapping');l.new(tc.outputs['Generated'],mp.inputs['Vector'])
 mp.inputs['Scale'].default_value=(1,40,3) if kind=='wood' else (2,2,2)
 nz=n.new('ShaderNodeTexNoise');nz.inputs['Scale'].default_value=3 if kind!='fabric' else 170;nz.inputs['Detail'].default_value=4;nz.inputs['Roughness'].default_value=.7;l.new(mp.outputs['Vector'],nz.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*c0,1);ramp.color_ramp.elements[1].color=(*c1,1);l.new(nz.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],b.inputs['Base Color'])
 if kind=='stone':
  wave=n.new('ShaderNodeTexWave');wave.inputs['Scale'].default_value=3;wave.inputs['Distortion'].default_value=11;wave.inputs['Detail'].default_value=5;l.new(mp.outputs['Vector'],wave.inputs['Vector']);l.new(nz.outputs['Fac'],ramp.inputs[0]);ramp.color_ramp.elements[0].position=.38;ramp.color_ramp.elements[1].position=.66
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.00045 if kind=='fabric' else .001;l.new(nz.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],b.inputs['Normal'])
 if kind=='fabric':b.inputs['Sheen Weight'].default_value=.05
 return m
CREAM=textured('Shedir02_Burro_colour_study',(.58,.52,.43),(.76,.70,.60),'fabric',.92)
GREY=textured('Torii_grey_fabric_code_pending',(.045,.05,.055),(.09,.10,.11),'fabric',.85)
WOOD=textured('Ernest_dark_wood_study',(.008,.004,.003),(.038,.018,.009),'wood',.32)
FLOOR=textured('Existing_grey_oak_approx',(.10,.085,.07),(.24,.21,.18),'wood',.34)
STONE=textured('Grigio_Orobico_procedural_not_scan',(.045,.048,.050),(.15,.13,.11),'stone',.23)
WHITE=textured('Carrara_procedural_not_scan',(.38,.39,.38),(.86,.85,.80),'stone',.24)
TILE=textured('Natural_stone_tile_unselected',(.24,.21,.17),(.37,.33,.27),'tile',.72)
RUG=textured('Shindo_Natural_material_study',(.40,.35,.26),(.62,.55,.42),'fabric',.9)
BLACK=mat('Black_Anthracite',(.022,.025,.028),.30,.78);BRONZE=mat('Golden_Brown',(.16,.105,.055),.27,.70)
WALL=mat('Warm_white_wall',(.72,.70,.66),.85);FRAME=mat('Window_dark_bronze',(.055,.052,.045),.34,.65)
def mesh(name,verts,faces,material):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);S.collection.objects.link(ob);ob.data.materials.append(material);return ob
def box(name,loc,size,material,bevel=.01):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:
  md=o.modifiers.new('Soft_edges','BEVEL');md.width=bevel;md.segments=5
  md=o.modifiers.new('Weighted_normals','WEIGHTED_NORMAL')
 return o
def cyl(name,loc,r,h,material,r2=None):
 bpy.ops.mesh.primitive_cone_add(vertices=64,radius1=r,radius2=r if r2 is None else r2,depth=h,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True;p.material_index=0
 md=o.modifiers.new('Edge_radius','BEVEL');md.width=.003;md.segments=3;return o
def line(name,pts,r,material):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=2;cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 ob=bpy.data.objects.new(name,cu);S.collection.objects.link(ob);ob.data.materials.append(material);return ob
def extrude(name,pts,z,h,material):
 n=len(pts);v=[(x,y,z) for x,y in pts]+[(x,y,z+h) for x,y in pts];f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 ob=mesh(name,v,f,material);md=ob.modifiers.new('Edge_radius','BEVEL');md.width=.006;md.segments=3;md=ob.modifiers.new('Normals','WEIGHTED_NORMAL');return ob
def roundedpts(w,d,r,steps=12):
 pts=[]
 for x,y,a in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
  for i in range(steps+1):t=math.radians(a+90*i/steps);pts.append((x+r*math.cos(t),y+r*math.sin(t)))
 return pts
def group(name,start,loc=(0,0,0),angle=0):
 root=bpy.data.objects.new(name,None);S.collection.objects.link(root)
 for ob in list(bpy.data.objects):
  if ob.name not in start and ob!=root and ob.parent is None:ob.parent=root
 root.location=loc;root.rotation_euler.z=math.radians(angle);return root
def mark(name,status,source,note=''):manifest.append(dict(item=name,geometry=status,source=source,note=note))
# Architecture: approximate plan envelope, same M coordinates.
floorpts=[(0,0),(9.4,0),(9.4,4.4),(7.15,4.4),(7.15,13.1),(4.88,13.1)]
extrude('LDK_floor',floorpts,-.14,.14,FLOOR)
arch.append(extrude('Ceiling',floorpts,2.70,.12,WALL))
# Fine long plank joints along x, 150mm spacing.
for i in range(88):
 y=i*.15;left=y*4.88/13.1;right=9.4 if y<4.4 else 7.15
 if left<right:line('Floor_joint',[(left,y,.001),(right,y,.001)],.0007,mat('joint'+str(i),(.12,.11,.09),.75))
for i in range(30):
 y=.075+i*.45;left=y*4.88/13.1;right=9.4 if y<4.4 else 7.15
 for x in [left+1.6+(i%3)*.6,left+4.0+(i%3)*.6]:
  if x<right:line('Plank_end',[(x,y-.075,.002),(x,y+.075,.002)],.0007,FRAME)
arch.append(box('TV_back_wall',(9.48,2.35,1.35),(.16,4.7,2.7),WALL))
arch.append(box('Kitchen_wall',(7.24,9.1,1.35),(.18,8.0,2.7),WALL))
arch.append(box('Hall_return',(8.25,4.50,1.35),(2.45,.18,2.7),WALL))
arch.append(box('Kitchen_top_wall',(6.03,13.2,1.35),(2.3,.18,2.7),WALL))
# Tile courses, natural stone proposal, no selected manufacturer.
for iy in range(5):
 for iz in range(3):box('TV_natural_tile',(9.385,.34+iy*.82,.45+iz*.9),(.02,.815,.895),TILE,.002)
# Window frames, clear open glazing in the study to keep views readable.
def glazing(a,b,n):
 length=(Vector(b)-Vector(a)).length
 for t in [i/n for i in range(n+1)]:
  p=Vector(a).lerp(Vector(b),t);box('Glazing_mullion',(p.x,p.y,1.35),(.045,.045,2.7),FRAME,.002)
 for z in [.025,2.66]:line('Window_rail',[(a[0],a[1],z),(b[0],b[1],z)],.025,FRAME)
glazing((0,0),(9.4,0),6);glazing((0,0),(4.88,13.1),8)
# Outside scenery is a context image from the supplied room photo, not a calibrated panorama.
contextpath=O/'window_context.jpg'
if contextpath.exists():
 m=bpy.data.materials.new('Supplied_photo_outside_context');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear();tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(contextpath));em=n.new('ShaderNodeEmission');em.inputs[1].default_value=.65;out=n.new('ShaderNodeOutputMaterial');l.new(tex.outputs['Color'],em.inputs[0]);l.new(em.outputs[0],out.inputs[0])
 def context_plane(name,vs):
  ob=mesh(name,vs,[(0,1,2,3)],m);uv=ob.data.uv_layers.new(name='UVMap')
  for loop,co in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=co
  ob.visible_shadow=False;return ob
 context_plane('Balcony_outside_photo',[(25,-6,-1),(-20,-6,-1),(-20,-6,5),(25,-6,5)])
 context_plane('Diagonal_outside_photo',[(-12,-22,-1),(3,30,-1),(3,30,5),(-12,-22,5)])
# Kitchen joinery and island footprint from the plan.
island=[((x-24)/35.2,(473-y)/35.2) for x,y in [(159,230),(201,114),(216,120),(194,242)]]
extrude('Existing_island_cabinet',island,0,.86,WOOD);extrude('Existing_island_white_top',island,.86,.05,WHITE)
for i in range(9):box('Kitchen_cabinet',(6.77,6.6+i*.70,.43),(.64,.69,.86),WOOD,.003)
box('Kitchen_wall_counter',(6.74,9.3,.89),(.72,6.15,.05),WHITE,.005)
box('Sink',(5.02,8.45,.916),(.43,.65,.016),BLACK,.04)
line('Faucet',[(5.0,8.48,.92),(5.0,8.48,1.20),(4.94,8.48,1.26),(4.80,8.48,1.26),(4.76,8.48,1.20)],.014,BLACK)
# Shindo rug. Relief stripe effect, not a scanned product texture.
x0,y0,x1,y1=C['rug']['rect'];box('Shindo_Natural_3500x4000',((x0+x1)/2,(y0+y1)/2,.008),(x1-x0,y1-y0,.016),RUG,.008)
for j in range(17):box('Shindo_subtle_woven_band',((x0+x1)/2,y0+.12+j*.23,.017),(x1-x0-.03,.012,.0015),RUG,.001)
mark('Shindo','dimensioned material study','https://www.poliform.it/us/products/shindo/','3500x4000mm provisional; pattern approximate')
# Ernest modules: soft pillow volumes rather than final boxes.
sofa=next(i for i in C['items'] if i['id']=='sofa')
for m in sofa['modules']:
 x0,y0,x1,y1=m['rect'];w=x1-x0;dep=y1-y0;cx=(x0+x1)/2;cy=(y0+y1)/2
 if m['id']=='F':
  box('Ernest_rear_table',(cx,cy,.36),(w,dep,.045),WOOD,.045);box('Rear_table_support',(cx,cy,.18),(.16,.62,.36),WOOD,.025);continue
 box('Ernest_plinth',(cx,cy,.08),(w-.15,dep-.15,.13),BLACK,.05)
 box('Ernest_lower_pillow',(cx,cy,.25),(w-.012,dep-.012,.34),CREAM,.14)
 # seam follows the seat perimeter.
 seam=[(cx+u,cy+v,.36) for u,v in roundedpts(w-.025,dep-.025,min(.14,w/4,dep/4))];line('Ernest_piping',seam+[seam[0]],.0022,CREAM)
 if m['id'] in 'ABC':
  ob=box('Ernest_soft_back',(x0+.19,cy,.515),(.36,dep-.025,.32),CREAM,.14);ob.rotation_euler.y=math.radians(-8)
mark('Ernest sofa','custom study from official module sizes','https://s3.poliform.it/2025/04/Poliform_catalog_ERNEST_2024.pdf','Official model awaits authenticated access; curves/seams approximate')
# The actual official 2D coffee-table outlines, extruded with study bases.
for i,t in enumerate(C['living_tables']['items']):
 pts=t['outline_xy'];extrude('Ernest_official_outline_top_'+str(i),pts,.267,.033,WOOD)
 xs=[p[0] for p in pts];ys=[p[1] for p in pts];xx=(min(xs)+max(xs))/2;yy=(min(ys)+max(ys))/2
 box('Ernest_blade_leg',(xx,yy,.135),(.12,.48,.27),WOOD,.045)
mark('Ernest coffee tables','official PDF outline extruded; base reconstructed','https://s3.poliform.it/2025/04/Poliform_catalog_ERNEST_2024.pdf','1200x900 +1200x700 stagger preserved')
# Linha Dining: dimensions + technical-sheet construction.
di=next(i for i in C['items'] if i['id']=='dining');st=set(bpy.data.objects.keys())
extrude('Linha_Grigio_Orobico_top',roundedpts(2.60,1.15,.13),.724,.016,STONE)
box('Linha_black_subframe',(0,0,.695),(2.25,.84,.042),BLACK,.006)
for x in [-.83,.83]:box('Linha_Golden_Brown_leg',(x,0,.34),(.20,.72,.68),BRONZE,.008)
group('Linha_Dining',st,(*di['center'],0),di['angle'])
mark('Linha Dining','technical drawing reconstruction','https://www.minotti.com/en/linha-dining','2600x1150x740; Golden Brown official; Grigio procedural')
# Torii: curved upholstered shell with stitch channels; fixed bronze legs.
def torii():
 for x in [-.235,.235]:
  for y in [-.23,.23]:line('Torii_bronze_leg',[(x,y,.015),(x*.96,y*.94,.52)],.0125,BRONZE)
 for x in [-.235,.235]:line('Torii_kigumi_rail',[(x,-.29,.39),(x,.30,.39)],.0125,BRONZE)
 seat=extrude('Torii_seat',roundedpts(.59,.57,.16),.435,.105,GREY)
 # U-shaped shell: front is local -Y; arms descend toward front.
 path=[]
 for i in range(49):
  th=math.radians(-8+i*196/48);x=.285*math.cos(th);y=.255*math.sin(th);z=.71+.105*math.sin(th);path.append((x,y,z))
 verts=[]
 for x,y,z in path:
  for k in range(10):
   an=2*math.pi*k/10;rad=.045;verts.append((x+rad*math.cos(an),y+rad*math.sin(an),z+.055*math.cos(an)))
 faces=[]
 for j in range(len(path)-1):
  for k in range(10):faces.append((j*10+k,j*10+(k+1)%10,(j+1)*10+(k+1)%10,(j+1)*10+k))
 ob=mesh('Torii_curved_back_top',verts,faces,GREY)
 # broad upholstered back panels, vertical stitched channels
 for j in range(24):
  th=math.radians(j*180/23);x=.275*math.cos(th);y=.248*math.sin(th);zt=.71+.105*math.sin(th)
  ob=box('Torii_vertical_back_channel',(x,y,(zt+.52)/2),(.073,.075,zt-.50),GREY,.03);ob.rotation_euler.z=th
 line('Torii_piping',path,.0025,BLACK)
for j,ch in enumerate(C['chairs']['items']):
 st=set(bpy.data.objects.keys());torii();group('Torii_fixed_'+str(j),st,(*ch['center'],0),di['angle']+(180 if ch['side_sign']<0 else 0))
mark('Torii Dining','dimensioned study reconstruction','https://www.minotti.com/en/torii-dining','640x660x870 envelope; grey fabric; official file awaiting login')
# Le Club, continuous tubular back/arms and thick rounded seat.
ch=C['lounge']['chairs'][0];st=set(bpy.data.objects.keys())
box('LeClub_underseat',(0,0,.18),(.76,.74,.28),CREAM,.135)
box('LeClub_seat',(0,-.04,.29),(.82,.78,.22),CREAM,.105)
path=[]
for j in range(61):
 t=math.radians(-12+j*204/60);path.append((.355*math.cos(t),.29*math.sin(t),.49+.065*math.sin(t)))
# continuous elliptical upholstered tube, broad vertical section
verts=[];faces=[]
for j,(x,y,z) in enumerate(path):
 t=math.radians(-12+j*204/60)
 for k in range(20):a=2*math.pi*k/20;verts.append((x+.105*math.cos(a)*math.cos(t),y+.105*math.cos(a)*math.sin(t),z+.11*math.sin(a)))
for j in range(60):
 for k in range(20):faces.append((j*20+k,j*20+(k+1)%20,(j+1)*20+(k+1)%20,(j+1)*20+k))
ob=mesh('LeClub_continuous_upholstered_shell',verts,faces,CREAM)
for p in ob.data.polygons:p.use_smooth=True
group('LeClub_window_facing',st,(*ch['center'],0),ch['angle']+180)
mark('Le Club','reference reconstruction','https://www.poliform.it/en/products/le-club-armchairs/','940x880x670 target; original model awaits access')
# IVRESSE side table, radial undulating metal blades.
tx,ty=C['lounge']['table']['center'];cyl('IVRESSE_Carrara_top',(tx,ty,.535),.30,.03,WHITE)
cyl('IVRESSE_black_chrome_base',(tx,ty,.013),.205,.026,BLACK)
for j in range(8):
 th=j*math.pi/4;v=[]
 for z,r in [(0.03,.16),(.13,.085),(.30,.065),(.43,.10),(.52,.16)]:v.extend([(tx,ty,z),(tx+r*math.cos(th),ty+r*math.sin(th),z)])
 ob=mesh('IVRESSE_radial_blade',v,[(k,k+1,k+3,k+2) for k in range(0,8,2)],BLACK);md=ob.modifiers.new('Steel_thickness','SOLIDIFY');md.thickness=.005
mark('IVRESSE','technical/reference reconstruction','https://technicals.roche-bobois.com/M66231103/TSv_IVRESSE_2017(2).pdf','600x550mm white Carrara')
# TV actual outer dimensions. Screen off for material/placement study.
box('LG_OLED83G6PJA',(9.345,2.35,1.38),(.028,1.847,1.057),BLACK,.008)
screen=mat('OLED_screen_off',(.005,.008,.012),.10,.18)
box('OLED_glass',(9.326,2.35,1.38),(.003,1.825,1.034),screen,.004)
mark('LG83G6','dimensioned exterior','User product screenshot','1847x1057x28mm; wall height provisional')
# Official B&O mesh imports. OBJ units mm, Y up. All parts share assembly origin.
def import_obj(path,material):
 bpy.ops.wm.obj_import(filepath=str(path),forward_axis='NEGATIVE_Z',up_axis='Y',global_scale=.001)
 obs=list(bpy.context.selected_objects)
 for o in obs:
  if o.type=='MESH':
   o.data.materials.clear();o.data.materials.append(material)
   for p in o.data.polygons:p.use_smooth=True;p.material_index=0
 return obs
basepath=R/'models/beolab28/Beolab 28/obj';DARKWOOD=textured('Charcoal_stained_oak',(.016,.014,.012),(.07,.06,.045),'wood',.40)
spobs=[]
for fn,ma in [('beolab-28_woofer_floor.obj',BLACK),('beolab-28_tube_basic.obj',BLACK),('beolab-28_fabric_curtain_off.obj',GREY),('beolab-28_wooden_curtain_off.obj',DARKWOOD)]:spobs+=import_obj(basepath/fn,ma)
for j,it in enumerate([i for i in C['items'] if i['id'].startswith('speaker')]):
 root=bpy.data.objects.new('Beolab28_OFFICIAL_'+str(j),None);S.collection.objects.link(root);root.location=(*it['center'],0);root.rotation_euler.z=math.radians(-90)
 for src in spobs:
  o=src.copy();o.data=src.data;S.collection.objects.link(o);o.parent=root
for src in spobs:bpy.data.objects.remove(src,do_unlink=True)
mark('Beolab28 pair','OFFICIAL OBJ','https://support.bang-olufsen.com/hc/en-us/articles/360020100498-Beolab-28','Floor/tube/fabric/wood supplied assemblies; materials recreated')
balancefiles=[p for p in (R/'models/balance').rglob('*.obj') if not p.name.startswith('._')]
if balancefiles:
 obs=import_obj(balancefiles[0],GREY);bpy.context.view_layer.update()
 bounds=[o.matrix_world@Vector(v) for o in obs for v in o.bound_box];lo=Vector(tuple(min(p[i] for p in bounds) for i in range(3)));hi=Vector(tuple(max(p[i] for p in bounds) for i in range(3)));scale=.38/(hi.z-lo.z)
 root=bpy.data.objects.new('Beosound_Balance_OFFICIAL',None);S.collection.objects.link(root)
 for ob in obs:ob.location-=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));ob.parent=root
 root.scale=(scale,scale,scale);root.location=(5.12,10.13,.91)
 mark('Beosound Balance','OFFICIAL OBJ','https://support.bang-olufsen.com/hc/en-us/articles/360041238491-Beosound-Balance','Finish not selected, temporary grey')
# Soft lighting through both window walls.
world=bpy.data.worlds.new('Daylight');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.80,.92,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45;S.world=world
def area(name,loc,target,power,size):
 ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;ob=bpy.data.objects.new(name,ld);S.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
area('Balcony_daylight',(4.5,-3,4.2),(5,4,0),1600,7)
area('Diagonal_daylight',(-1,6.5,4.8),(5,4,.5),1800,8)
area('Ceiling_bounce',(5,5,5),(5,4,0),700,6)
ld=bpy.data.lights.new('Morning_sun','SUN');ld.energy=1.4;ld.angle=.06;ob=bpy.data.objects.new('Morning_sun',ld);S.collection.objects.link(ob);ob.rotation_euler=(math.radians(28),math.radians(-22),math.radians(-30))
def camera(name,loc,target,lens=26,ortho=None):
 data=bpy.data.cameras.new(name);data.lens=lens;ob=bpy.data.objects.new(name,data);S.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
 if ortho:data.type='ORTHO';data.ortho_scale=ortho
 return ob
cameras=[camera('01_living_TV',(2.75,5.6,1.65),(7.45,2.2,1.0),22),camera('02_living_windows',(8.6,4.1,1.65),(3.7,2.1,.9),22),camera('03_dining',(6.7,7.0,1.65),(3.6,4.9,.85),25),camera('04_lounge',(3.8,3.45,1.4),(1.65,1.25,.65),34),camera('05_plan_axon',(-10,-14,17),(5.0,5.0,.5),ortho=17)]
S.camera=cameras[0]
(O/'model_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Harajuku_LDK_M.blend'))
if '--build-only' not in sys.argv:
 cams=cameras[:1] if '--preview' in sys.argv else cameras
 if '--preview' in sys.argv:S.render.resolution_percentage=50;S.cycles.samples=12
 for cam in cams:
  S.camera=cam
  for ob in arch:ob.hide_render=(cam.name=='05_plan_axon')
  S.render.filepath=str(O/(cam.name+('_preview' if '--preview' in sys.argv else '')+'.png'));bpy.ops.render.render(write_still=True)
print('SCENE_COMPLETE',len(bpy.data.objects),flush=True)
