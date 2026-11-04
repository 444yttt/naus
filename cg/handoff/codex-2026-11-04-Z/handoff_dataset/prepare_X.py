from pathlib import Path
import bpy,json,math,sys,hashlib
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parent;W=R/'out/photo_final_W';O=R/'out_X';args=sys.argv[sys.argv.index('--')+1:];shot=args[0]
bpy.ops.wm.open_mainfile(filepath=str(W/f'{shot}_photo_scene.blend'));S=bpy.context.scene
def hull(ps):
 p=sorted(set((round(v[0],7),round(v[1],7)) for v in ps))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[];hi=[]
 for v in p:
  while len(lo)>=2 and cross(lo[-2],lo[-1],v)<=0:lo.pop()
  lo.append(v)
 for v in p[::-1]:
  while len(hi)>=2 and cross(hi[-2],hi[-1],v)<=0:hi.pop()
  hi.append(v)
 return lo[:-1]+hi[:-1]
def poly_dist(a,b):
 def pd(p,u,v):
  p,u,v=Vector(p),Vector(u),Vector(v);d=v-u;t=max(0,min(1,(p-u).dot(d)/d.length_squared));return (p-u-t*d).length
 return min([pd(p,b[j],b[(j+1)%len(b)]) for p in a for j in range(len(b))]+[pd(p,a[j],a[(j+1)%len(a)]) for p in b for j in range(len(a))])
def overlap(a,b):
 # SAT for convex projected footprints. Edge contact is not penetration.
 for p in [a,b]:
  for j,u in enumerate(p):
   v=p[(j+1)%len(p)];n=Vector((u[1]-v[1],v[0]-u[0]));aa=[Vector(q).dot(n) for q in a];bb=[Vector(q).dot(n) for q in b]
   if min(max(aa),max(bb))-max(min(aa),min(bb))<=1e-6:return False
 return True
def footprint(obs):return hull([tuple((ob.matrix_world@v.co)[:2]) for ob in obs for v in ob.data.vertices])
root=bpy.data.objects['Linha_Dining_THIRDPARTY_260'];table=[o for o in S.objects if o.type=='MESH' and o.name.startswith('Linha_Warehouse')]
ip=[((x-24)/35.2,(473-y)/35.2) for x,y in [(159,230),(194,242),(216,182),(216,120),(201,114)]];island=hull(ip);before=footprint(table);oldcenter=root.location.copy();oldangle=root.rotation_euler.z
a,b=Vector(ip[0]),Vector(ip[1]);t=(b-a).normalized();n=Vector((-t.y,t.x));angle=math.atan2(n.y,n.x);delta=angle-oldangle
rot=Matrix.Rotation(delta,4,'Z');pivot=Matrix.Translation(oldcenter)
T=pivot@rot@pivot.inverted()
roots=[root]+[bpy.data.objects[f'Torii_USER_MODEL_{i}'] for i in range(6)]
for ob in roots:ob.matrix_world=T@ob.matrix_world
bpy.context.view_layer.update();newfoot=footprint(table);maximum=max(Vector(p).dot(n) for p in newfoot)
# Move the actual end envelope to a 2mm gap; centre it on the island end.
rootxy=Vector(root.location[:2]);target=(a+b)/2;shift=n*(target.dot(n)-maximum-.002)+t*(target.dot(t)-rootxy.dot(t))
for ob in roots:ob.location.x+=shift.x;ob.location.y+=shift.y
bpy.context.view_layer.update();after=footprint(table)
checks=[]
for j in range(6):
 rr=bpy.data.objects[f'Torii_USER_MODEL_{j}'];ch=[o for o in S.objects if o.type=='MESH' and o.parent==rr];p=footprint(ch)
 # Exact footprint vs fixed island; glazing signed distance to raster segment.
 ga=Vector(((24-24)/35.2,(473-473)/35.2));gb=Vector(((194-24)/35.2,(473-14)/35.2));gd=(gb-ga).normalized();gn=Vector((gd.y,-gd.x));glass=min((Vector(q)-ga).dot(gn) for q in p)
 checks.append({'chair':j,'island_penetration':overlap(p,island),'island_clearance_m':poly_dist(p,island),'glazing_clearance_m':glass,'room_right_clearance_m':9.4-max(q[0] for q in p),'room_bottom_clearance_m':min(q[1] for q in p),'outline_xy':p})
if any(v['island_penetration'] or v['glazing_clearance_m']<.04 or v['room_right_clearance_m']<0 or v['room_bottom_clearance_m']<0 for v in checks):
 (O/'STOP_layout_collision.json').write_text(json.dumps(checks,indent=2));raise RuntimeError('Chair interference: see STOP_layout_collision.json')
placement={'before_gap_m':poly_dist(before,island),'after_gap_m':poly_dist(after,island),'rotation_delta_deg':math.degrees(delta),'angle_deg':math.degrees(angle),'translation_after_rotation_m':list(shift),'root_center_before':list(oldcenter),'root_center_after':list(root.location),'window_correction_m':0,'chair_checks':checks,'table_outline_before':before,'table_outline_after':after,'island_outline':island,'status':'exact source-mesh footprint against approximate room plan proxy, not measured room'}
(O/f'{shot}_placement_X.json').write_text(json.dumps(placement,indent=2))
assert .0005<placement['after_gap_m']<.004 and not overlap(after,island)
def preview_stage(label):
 if '--stages' not in args:return
 S.render.use_border=False;S.render.use_crop_to_border=False;S.render.resolution_percentage=12;S.cycles.samples=16
 for nd in S.node_tree.nodes:
  if nd.type=='OUTPUT_FILE':nd.mute=True
 S.render.filepath=str(O/f'previews/{shot}_{label}.png');bpy.ops.render.render(write_still=True)
preview_stage('01_placement')
# Additional broad ceiling/window return, common to all cameras. Original four
# lights are unchanged. It illuminates the Eames rear and its floor reflection.
ld=bpy.data.lights.new('Eames_ceiling_return_X','AREA');ld.energy=180;ld.color=(1.0,.94,.84);ld.shape='DISK';ld.size=2.4
ob=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(ob);ob.location=(3.1,1.7,2.38);ob.rotation_euler=(Vector((1.7,1.85,.45))-ob.location).to_track_quat('-Z','Y').to_euler()
ld.specular_factor=0;ob.visible_glossy=False
for ma in bpy.data.materials:
 if ma.name.startswith('Eames_dark_wood_refined'):
  bs=ma.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.025,.014,.009,1);bs.inputs['Roughness'].default_value=.38
  bs.inputs['Coat Weight'].default_value=.12;bs.inputs['Coat Roughness'].default_value=.28
preview_stage('02_eames')
# Preserve the light upholstery hue. Increase seam depth using local geometry
# occlusion and introduce a restrained leather-like fine specular response.
ma=bpy.data.materials.get('Shedir02_Burro_colour_study');nn=ma.node_tree.nodes;ll=ma.node_tree.links;bs=nn.get('Principled BSDF')
old=bs.inputs['Base Color'].links[0].from_socket if bs.inputs['Base Color'].links else None
ao=nn.new('ShaderNodeAmbientOcclusion');ao.name='X_seam_local_geometry';ao.inputs['Distance'].default_value=.075;ao.samples=16;ao.only_local=True
mix=nn.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.58
if old:ll.new(old,mix.inputs[1])
else:mix.inputs[1].default_value=bs.inputs['Base Color'].default_value
ll.new(ao.outputs['AO'],mix.inputs[2]);ll.new(mix.outputs[0],bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value=.46;bs.inputs['Sheen Weight'].default_value=.10;bs.inputs['Coat Weight'].default_value=.13;bs.inputs['Coat Roughness'].default_value=.32
for nd in nn:
 if nd.type=='BUMP':nd.inputs['Strength'].default_value=.30;nd.inputs['Distance'].default_value=.00035
preview_stage('03_sofa')
# Camera shift implemented as physical sensor shift, preserving source photo.
c=json.loads((O/f'{shot}_camera.json').read_text());cam=S.camera
if shot in ['u2','p13']:
 cam.matrix_world=Matrix.Translation(c['C'])@(Matrix(c['R']).transposed()@Matrix(((1,0,0),(0,-1,0),(0,0,-1)))).to_4x4();cam.data.lens=c['f']*36/c['W'];cam.data.sensor_width=36;cam.data.sensor_fit='HORIZONTAL'
 cx,cy=c['principal_point_native_px'];cam.data.shift_x=-(cx-c['W']/2)/c['W'];cam.data.shift_y=(cy-c['H']/2)/c['W']
 bpy.context.view_layer.update()
 from bpy_extras.object_utils import world_to_camera_view
 for p,expected in zip(next(r for r in json.loads((O/'camera_fit_X.json').read_text()) if r['shot']==shot)['controls_world'],next(r for r in json.loads((O/'camera_fit_X.json').read_text()) if r['shot']==shot)['controls_projected_native_px']):
  q=world_to_camera_view(S,cam,Vector(p));assert abs(q.x*c['W']-expected[0])<.05 and abs((1-q.y)*c['H']-expected[1])<.05,('sensor shift sign',p,q,expected)
preview_stage('04_camera')
S.render.threads=10;S.render.use_border=True;S.render.border_min_x=0;S.render.border_max_x=1;S.render.border_min_y=0;S.render.border_max_y={'u1':.72,'u2':.62,'p09':.60,'p01':.56,'p13':.62}[shot];S.render.use_crop_to_border=False;S.render.resolution_percentage=100;S.cycles.samples=24;S.cycles.adaptive_threshold=.020;S.cycles.adaptive_min_samples=8;S.cycles.use_denoising=True
S.render.filepath=str(O/f'{shot}_full_foreground.png')
S.view_layers[0].use_pass_normal=True;S.view_layers[0].use_pass_object_index=True;S.view_layers[0].use_pass_material_index=True
for ma in bpy.data.materials:ma.pass_index=8 if ma.name=='Shedir02_Burro_colour_study' else 0
for ob in S.objects:
 ob.pass_index=8 if ob.type=='MESH' and any(sl.material and sl.material.name=='Shedir02_Burro_colour_study' for sl in ob.material_slots) else 9 if ob.name.startswith('SEAT-OUTER_SHELL') else 0
rl=next(nd for nd in S.node_tree.nodes if nd.type=='R_LAYERS')
for nd in S.node_tree.nodes:
 if nd.type=='OUTPUT_FILE':
  nd.mute=False;nd.base_path=str(O/f'{shot}_full_passes')
  for passname in ['Normal','IndexOB','IndexMA']:
   if passname not in nd.inputs:nd.file_slots.new(passname)
   S.node_tree.links.new(rl.outputs[passname],nd.inputs[passname])
bpy.ops.wm.save_as_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'))
print('X_PREPARED',shot,'gap_mm',placement['after_gap_m']*1000,'rotation',placement['rotation_delta_deg'],flush=True)
