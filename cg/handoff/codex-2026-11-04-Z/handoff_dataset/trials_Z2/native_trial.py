# Trial only: never saves the production blend. Renders p09 coffee-table region at 50%.
import bpy,sys
from pathlib import Path
R=Path('/work/hj/handoff_dataset');var=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.open_mainfile(filepath=str(R/'out_Z/p09_photo_scene.blend'));S=bpy.context.scene
old=bpy.data.materials['Ernest_dark_wood_study']
ramp=next(n for n in old.node_tree.nodes if n.type=='VALTORGB')
print('RAMP',[(round(e.position,3),tuple(round(c,4) for c in e.color)) for e in ramp.color_ramp.elements])
def wood(name,coat,coat_r,rough,grain_contrast,base_scale=1.0,gs=(55,2.2,55),dist=7,bump=.18,mixf=.35):
    global BUMP,MIXF;BUMP=bump;MIXF=mixf
    global GS,DIST;GS=gs;DIST=dist
    ma=bpy.data.materials.new(name);ma.use_nodes=True;nt=ma.node_tree;nn=nt.nodes;ll=nt.links
    bs=nn['Principled BSDF']
    tc=nn.new('ShaderNodeTexCoord');mp=nn.new('ShaderNodeMapping')
    # grain runs along the long (Y) axis of each table: stretch noise strongly along Y
    mp.inputs['Scale'].default_value=GS
    ll.new(tc.outputs['Object'],mp.inputs['Vector'])
    wv=nn.new('ShaderNodeTexWave');wv.wave_type='BANDS';wv.bands_direction='X';wv.inputs['Scale'].default_value=1.0;wv.inputs['Distortion'].default_value=DIST;wv.inputs['Detail'].default_value=6;wv.inputs['Detail Scale'].default_value=1.6;wv.inputs['Detail Roughness'].default_value=.62
    ll.new(mp.outputs['Vector'],wv.inputs['Vector'])
    nz=nn.new('ShaderNodeTexNoise');nz.inputs['Scale'].default_value=2.0;nz.inputs['Detail'].default_value=8;nz.inputs['Roughness'].default_value=.6
    ll.new(mp.outputs['Vector'],nz.inputs['Vector'])
    mx=nn.new('ShaderNodeMix');mx.data_type='FLOAT';mx.inputs['Factor'].default_value=MIXF
    ll.new(wv.outputs['Fac'],mx.inputs['A']);ll.new(nz.outputs['Fac'],mx.inputs['B'])
    cr=nn.new('ShaderNodeValToRGB');e=cr.color_ramp.elements
    lo=tuple(c*base_scale for c in (0.016,0.0105,0.0075));hi=tuple(c*base_scale*grain_contrast for c in (0.016,0.0105,0.0075))
    e[0].position=.25;e[0].color=lo+(1,);e[1].position=.75;e[1].color=hi+(1,)
    ll.new(mx.outputs['Result'],cr.inputs['Fac']);ll.new(cr.outputs['Color'],bs.inputs['Base Color'])
    rr=nn.new('ShaderNodeMapRange');rr.inputs['To Min'].default_value=rough-.06;rr.inputs['To Max'].default_value=rough+.08
    ll.new(mx.outputs['Result'],rr.inputs['Value']);ll.new(rr.outputs['Result'],bs.inputs['Roughness'])
    bp=nn.new('ShaderNodeBump');bp.inputs['Strength'].default_value=BUMP;bp.inputs['Distance'].default_value=.00025
    ll.new(mx.outputs['Result'],bp.inputs['Height']);ll.new(bp.outputs['Normal'],bs.inputs['Normal'])
    bs.inputs['Coat Weight'].default_value=coat;bs.inputs['Coat Roughness'].default_value=coat_r;bs.inputs['IOR'].default_value=1.5
    ma.pass_index=10
    return ma
V={'K':dict(coat=.30,coat_r=.18,rough=.42,grain_contrast=1.8,base_scale=1.3,gs=(30,1.6,30),dist=9,bump=.05,mixf=.5),
   'L':dict(coat=.30,coat_r=.18,rough=.42,grain_contrast=2.1,base_scale=1.25,gs=(30,1.6,30),dist=6,bump=.08,mixf=.5),
   'G':dict(coat=.30,coat_r=.18,rough=.42,grain_contrast=2.8,base_scale=1.25,gs=(30,1.6,30),dist=9),
   'E':dict(coat=.30,coat_r=.18,rough=.42,grain_contrast=3.0,base_scale=1.25,gs=(16,1.2,16),dist=14),
   'F':dict(coat=.22,coat_r=.22,rough=.46,grain_contrast=3.4,base_scale=1.35,gs=(12,1.0,12),dist=18),
   'B':dict(coat=.25,coat_r=.12,rough=.38,grain_contrast=2.6),
   'C':dict(coat=.45,coat_r=.07,rough=.34,grain_contrast=2.6),
   'D':dict(coat=.30,coat_r=.18,rough=.42,grain_contrast=3.2,base_scale=1.25)}
if var!='A':
    ma=wood('Ernest_dark_wood_grain_trial_'+var,**V[var])
    for n in ['Ernest_DEALER_FBX_table_0','Ernest_DEALER_FBX_table_1','Ernest_rear_table']:
        o=bpy.data.objects[n]
        for s in o.material_slots:
            if s.material==old:s.material=ma
W,H=S.render.resolution_x,S.render.resolution_y;x0,y0,x1,y1=350,2700,1350,3300
S.render.resolution_percentage=100;S.render.use_border=True;S.render.use_crop_to_border=True
S.render.border_min_x=x0/W;S.render.border_max_x=x1/W;S.render.border_min_y=1-y1/H;S.render.border_max_y=1-y0/H
S.render.threads_mode='AUTO'
for nd in S.node_tree.nodes:
    if nd.type=='OUTPUT_FILE':nd.mute=True
S.render.filepath=f'/work/trial/native_{var}.png';bpy.ops.render.render(write_still=True);print('TRIAL_DONE',var)
