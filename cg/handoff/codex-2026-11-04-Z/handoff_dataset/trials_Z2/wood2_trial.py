import bpy,sys
from pathlib import Path
R=Path('/work/hj/handoff_dataset');var=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.open_mainfile(filepath=str(R/'out_Z/p09_photo_scene.blend'));S=bpy.context.scene
V={'H':dict(c=1.7,bump=.05,fine=(90,2.5,90),coarse=(14,.9,14),mixf=.55,coat=.30,coat_r=.18,rough=.42,base=1.25),
   'I':dict(c=1.45,bump=.035,fine=(120,3,120),coarse=(18,1.1,18),mixf=.6,coat=.30,coat_r=.16,rough=.40,base=1.3),
   'J':dict(c=2.0,bump=.06,fine=(70,2,70),coarse=(10,.8,10),mixf=.5,coat=.28,coat_r=.2,rough=.44,base=1.2)}[var]
def build(p):
    ma=bpy.data.materials.new('wood2_'+var);ma.use_nodes=True;nn=ma.node_tree.nodes;ll=ma.node_tree.links;bs=nn['Principled BSDF']
    tc=nn.new('ShaderNodeTexCoord')
    def stretched(scale,detail,rough):
        mp=nn.new('ShaderNodeMapping');mp.inputs['Scale'].default_value=scale;ll.new(tc.outputs['Object'],mp.inputs['Vector'])
        nz=nn.new('ShaderNodeTexNoise');nz.inputs['Scale'].default_value=1.0;nz.inputs['Detail'].default_value=detail;nz.inputs['Roughness'].default_value=rough;nz.inputs['Distortion'].default_value=.4
        ll.new(mp.outputs['Vector'],nz.inputs['Vector']);return nz
    f=stretched(p['fine'],10,.65);c=stretched(p['coarse'],4,.5)
    mx=nn.new('ShaderNodeMix');mx.data_type='FLOAT';mx.inputs['Factor'].default_value=p['mixf'];ll.new(c.outputs['Fac'],mx.inputs['A']);ll.new(f.outputs['Fac'],mx.inputs['B'])
    cr=nn.new('ShaderNodeValToRGB');e=cr.color_ramp.elements;b=(0.016,0.0105,0.0075)
    e[0].position=.3;e[0].color=tuple(x*p['base'] for x in b)+(1,);e[1].position=.7;e[1].color=tuple(x*p['base']*p['c'] for x in b)+(1,)
    ll.new(mx.outputs['Result'],cr.inputs['Fac']);ll.new(cr.outputs['Color'],bs.inputs['Base Color'])
    rr=nn.new('ShaderNodeMapRange');rr.inputs['To Min'].default_value=p['rough']-.04;rr.inputs['To Max'].default_value=p['rough']+.06;ll.new(f.outputs['Fac'],rr.inputs['Value']);ll.new(rr.outputs['Result'],bs.inputs['Roughness'])
    bp=nn.new('ShaderNodeBump');bp.inputs['Strength'].default_value=p['bump'];bp.inputs['Distance'].default_value=.0002;ll.new(f.outputs['Fac'],bp.inputs['Height']);ll.new(bp.outputs['Normal'],bs.inputs['Normal'])
    bs.inputs['Coat Weight'].default_value=p['coat'];bs.inputs['Coat Roughness'].default_value=p['coat_r'];ma.pass_index=10;return ma
old=bpy.data.materials['Ernest_dark_wood_study'];ma=build(V)
for n in ['Ernest_DEALER_FBX_table_0','Ernest_DEALER_FBX_table_1','Ernest_rear_table']:
    for s in bpy.data.objects[n].material_slots:
        if s.material==old:s.material=ma
W,H=S.render.resolution_x,S.render.resolution_y;x0,y0,x1,y1=350,2700,1350,3300
S.render.resolution_percentage=100;S.render.use_border=True;S.render.use_crop_to_border=True
S.render.border_min_x=x0/W;S.render.border_max_x=x1/W;S.render.border_min_y=1-y1/H;S.render.border_max_y=1-y0/H;S.render.threads_mode='AUTO'
for nd in S.node_tree.nodes:
    if nd.type=='OUTPUT_FILE':nd.mute=True
S.render.filepath=f'/work/trial/wood2_{var}.png';bpy.ops.render.render(write_still=True);print('TRIAL_DONE',var)
