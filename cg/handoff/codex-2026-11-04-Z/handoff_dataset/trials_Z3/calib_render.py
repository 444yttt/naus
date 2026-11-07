import bpy,sys
out=sys.argv[sys.argv.index('--')+1];S=bpy.context.scene
static=('LDK_floor','TV_back_wall','Kitchen_wall','Hall_return','Kitchen_top_wall','Ceiling','Kitchen_cabinet','Kitchen_wall_counter','Existing_island','Sink','Faucet','Balcony_overhang','Window_frame_shadow_Z3')
m=bpy.data.materials.new('calib_white');m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.8,.8,.8,1);b.inputs['Roughness'].default_value=1;b.inputs['Specular IOR Level'].default_value=0
for o in S.objects:
    if o.type not in('MESH','CURVE'):continue
    if not o.name.startswith(static):o.hide_render=True;continue
    if o.name in('Ceiling','LDK_floor'):
        o.visible_camera=True;o.is_shadow_catcher=False;o.data.materials.clear();o.data.materials.append(m)
S.render.film_transparent=False;S.render.resolution_percentage=25;S.render.use_border=False;S.cycles.samples=32;S.cycles.use_denoising=True;S.render.threads_mode='AUTO'
S.view_settings.view_transform='Standard';S.view_settings.look='None';S.view_settings.exposure=0
S.render.image_settings.file_format='OPEN_EXR';S.render.image_settings.color_depth='32'
for nd in S.node_tree.nodes:
    if nd.type=='OUTPUT_FILE':nd.mute=True
S.render.filepath=out;bpy.ops.render.render(write_still=True);print('CALIB_DONE',out)
