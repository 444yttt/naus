# Diagnostic only: u2 Eames region, fabric emissive red, shells emissive green, no save.
import bpy
S=bpy.context.scene
def emi(name,c):
    m=bpy.data.materials.new(name);m.use_nodes=True;nn=m.node_tree.nodes;nn.clear()
    e=nn.new('ShaderNodeEmission');e.inputs[0].default_value=c+(1,);o=nn.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs[0]);return m
red=emi('dbg_red',(1,0,0));green=emi('dbg_green',(0,1,0));blue=emi('dbg_blue',(0,0,1))
keep={'SEAT-FABRIC (C-Group#4)':red,'SEAT-OUTER_SHELL_BOTTOM (C-Group#6)':green,'SEAT-OUTER_SHELL_BACK (C-Group#5)':blue}
for o in S.objects:
    if o.type in('MESH','CURVE'):
        if o.name in keep:
            o.data.materials.clear();o.data.materials.append(keep[o.name])
        elif not o.name.startswith('SEAT'):o.hide_render=True
S.render.resolution_percentage=100;S.render.use_border=True;S.render.use_crop_to_border=True
W,H=S.render.resolution_x,S.render.resolution_y
x0,y0,x1,y1=700,2250,1350,2800
S.render.border_min_x=x0/W;S.render.border_max_x=x1/W;S.render.border_min_y=1-y1/H;S.render.border_max_y=1-y0/H
S.cycles.samples=4;S.cycles.use_denoising=False;S.render.threads_mode='AUTO'
S.view_settings.view_transform='Standard';S.view_settings.exposure=0
for nd in S.node_tree.nodes:
    if nd.type=='OUTPUT_FILE':nd.mute=True
S.render.filepath='/work/trial/eames_diag.png';bpy.ops.render.render(write_still=True);print('DIAG_DONE')
