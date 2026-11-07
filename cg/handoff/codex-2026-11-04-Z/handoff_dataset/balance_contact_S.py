"""Native-resolution differential contact-lighting crop for Balance on the photo island."""
import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_S'
bpy.ops.wm.open_mainfile(filepath=str(O/'p13_photo_scene.blend'))
S=bpy.context.scene;S.cycles.samples=64;S.cycles.adaptive_threshold=.015
S.render.resolution_percentage=100;S.render.use_border=True;S.render.use_crop_to_border=True
W,H=3024,4032;rect=[1740,1980,2110,2380];a,b,aa,bb=rect
S.render.border_min_x=a/W;S.render.border_max_x=aa/W;S.render.border_min_y=(H-bb)/H;S.render.border_max_y=(H-b)/H
static=('LDK_floor','TV_back_wall','Kitchen_wall','Hall_return','Kitchen_top_wall','Ceiling','Kitchen_cabinet','Kitchen_wall_counter','Existing_island','Sink','Faucet','Balcony_overhang','Balcony_reflection_photo','Diagonal_reflection_photo')
balance=[]
for ob in S.objects:
 if ob.type not in ['MESH','CURVE']:continue
 par=ob;belongs=False
 while par:
  if par.name=='Beosound_Balance_OFFICIAL':belongs=True;break
  par=par.parent
 if belongs:balance.append(ob);ob.hide_render=False
 elif not ob.name.startswith(static):ob.hide_render=True
island=bpy.data.objects.get('Existing_island_photo_proxy');island.is_shadow_catcher=True;island.visible_camera=True
S.use_nodes=True;nn=S.node_tree.nodes;ll=S.node_tree.links;nn.clear();rl=nn.new('CompositorNodeRLayers');co=nn.new('CompositorNodeComposite');ll.new(rl.outputs['Image'],co.inputs[0])
fo=nn.new('CompositorNodeOutputFile');fo.format.file_format='OPEN_EXR_MULTILAYER';fo.format.color_depth='16'
while fo.inputs:fo.file_slots.remove(fo.inputs[0])
for k in ['Image','Shadow Catcher']:
 fo.file_slots.new(k);ll.new(rl.outputs[k],fo.inputs[k])
S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGBA'
for stage in ['with','bare']:
 for ob in balance:ob.hide_render=(stage=='bare')
 fo.base_path=str(O/f'p13_balance_contact_{stage}_passes');S.render.filepath=str(O/f'p13_balance_contact_{stage}.png')
 bpy.ops.render.render(write_still=True)
(O/'p13_balance_contact.json').write_text(json.dumps({'rect':rect,'W':W,'H':H,'samples':64,'method':'native differential shadow-catcher ratio on island top, same calibrated camera and source lights; furniture other than Balance removed for this local receiver study'},indent=2),encoding='utf8')
print('BALANCE_CONTACT_COMPLETE')
