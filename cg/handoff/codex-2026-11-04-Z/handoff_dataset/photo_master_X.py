"""Pack a private editable project with all approved photographic cameras."""
import bpy,json
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parent;O=R/'out_X'
bpy.ops.wm.open_mainfile(filepath=str(O/'u1_photo_scene.blend'));s=bpy.context.scene
island=bpy.data.objects.get('Existing_island_plan_proxy')
if island:island.visible_camera=True;island.is_shadow_catcher=True
for shot in ['u1','u2','p09','p01','p13']:
    c=json.loads((O/f'{shot}_camera.json').read_text(encoding='utf8'))
    ob=bpy.data.objects.get('PhotoMatched_'+shot)
    if ob is None:
        data=bpy.data.cameras.new('PhotoMatched_'+shot);ob=bpy.data.objects.new('PhotoMatched_'+shot,data);s.collection.objects.link(ob)
    data=ob.data;data.sensor_fit='HORIZONTAL';data.sensor_width=36;data.lens=c['f']*36/c['W'];data.clip_start=.03;data.clip_end=200
    cx,cy=c.get('principal_point_native_px',[c['W']/2,c['H']/2]);data.shift_x=-(cx-c['W']/2)/c['W'];data.shift_y=(cy-c['H']/2)/c['W']
    ob.matrix_world=Matrix.Translation(c['C'])@(Matrix(c['R']).transposed()@Matrix(((1,0,0),(0,-1,0),(0,0,-1)))).to_4x4()
    data.show_background_images=True;data.background_images.clear()
    bg=data.background_images.new();bg.image=bpy.data.images.load(str(R/f'images/photos_srgb/{shot}.png'),check_existing=True);bg.alpha=.65;bg.display_depth='BACK';bg.frame_method='FIT'
    ob['photo_width']=c['W'];ob['photo_height']=c['H'];ob['photo_source']=f'{shot}.jpg'
    ob['note']='Switch scene resolution to photo_width × photo_height when changing camera. Final photographic composition is performed by photo_composite_X.py.'
s.camera=bpy.data.objects['PhotoMatched_u1'];s.render.use_border=False;s.render.use_crop_to_border=False
s.render.filepath='//renders/foreground.png'
for node in s.node_tree.nodes:
    if node.type=='OUTPUT_FILE':node.base_path='//renders/passes/'
txt=bpy.data.texts.new('DELIVERY_README')
txt.write('Private editable geometry project. All cameras use one common furniture layout. ICC-converted photographic underlays are packed.\nThe final JPEG/PNG files include shadow normalization and separate five-pass floor reflection and directional occlusion; rendering this blend alone does not reproduce those composite operations.\nLighting, camera matching and room scale are photographic estimates, not measured HDR/material/survey data.\n')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'Harajuku_LDK_X.blend'))
print('EDITABLE_PROJECT_SAVED')
