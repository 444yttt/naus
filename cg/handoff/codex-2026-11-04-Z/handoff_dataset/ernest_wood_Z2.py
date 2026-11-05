"""Z2 Ernest dark-wood finish for the two front tables and the integrated rear table only.
Chosen after p09 trials A(current Z)/B-G at 50% and G/H/I/J/K/L at native 1:1; K adopted (G's
stronger grain read as a ribbed pattern at 1:1): visible open grain along each
table, soft coat sheen. Kitchen cabinet proxies keep 'Ernest_dark_wood_study' (shared before)."""
import bpy
BASE=(0.016,0.0105,0.0075)
TARGETS=['Ernest_DEALER_FBX_table_0','Ernest_DEALER_FBX_table_1','Ernest_rear_table']
P=dict(coat=.30,coat_r=.18,rough=.42,grain_contrast=1.8,base_scale=1.3,gs=(30,1.6,30),dist=9,bump=.05,mixf=.5)
def build():
    ma=bpy.data.materials.new('Ernest_dark_wood_grain_Z2');ma.use_nodes=True;nt=ma.node_tree;nn=nt.nodes;ll=nt.links;bs=nn['Principled BSDF']
    tc=nn.new('ShaderNodeTexCoord');mp=nn.new('ShaderNodeMapping');mp.inputs['Scale'].default_value=P['gs'];ll.new(tc.outputs['Object'],mp.inputs['Vector'])
    wv=nn.new('ShaderNodeTexWave');wv.wave_type='BANDS';wv.bands_direction='X';wv.inputs['Scale'].default_value=1.0;wv.inputs['Distortion'].default_value=P['dist'];wv.inputs['Detail'].default_value=6;wv.inputs['Detail Scale'].default_value=1.6;wv.inputs['Detail Roughness'].default_value=.62
    ll.new(mp.outputs['Vector'],wv.inputs['Vector'])
    nz=nn.new('ShaderNodeTexNoise');nz.inputs['Scale'].default_value=2.0;nz.inputs['Detail'].default_value=8;nz.inputs['Roughness'].default_value=.6;ll.new(mp.outputs['Vector'],nz.inputs['Vector'])
    mx=nn.new('ShaderNodeMix');mx.data_type='FLOAT';mx.inputs['Factor'].default_value=P['mixf'];ll.new(wv.outputs['Fac'],mx.inputs['A']);ll.new(nz.outputs['Fac'],mx.inputs['B'])
    cr=nn.new('ShaderNodeValToRGB');e=cr.color_ramp.elements;base=BASE
    e[0].position=.25;e[0].color=tuple(c*P['base_scale'] for c in base)+(1,);e[1].position=.75;e[1].color=tuple(c*P['base_scale']*P['grain_contrast'] for c in base)+(1,)
    ll.new(mx.outputs['Result'],cr.inputs['Fac']);ll.new(cr.outputs['Color'],bs.inputs['Base Color'])
    rr=nn.new('ShaderNodeMapRange');rr.inputs['To Min'].default_value=P['rough']-.06;rr.inputs['To Max'].default_value=P['rough']+.08;ll.new(mx.outputs['Result'],rr.inputs['Value']);ll.new(rr.outputs['Result'],bs.inputs['Roughness'])
    bp=nn.new('ShaderNodeBump');bp.inputs['Strength'].default_value=P['bump'];bp.inputs['Distance'].default_value=.00025;ll.new(mx.outputs['Result'],bp.inputs['Height']);ll.new(bp.outputs['Normal'],bs.inputs['Normal'])
    bs.inputs['Coat Weight'].default_value=P['coat'];bs.inputs['Coat Roughness'].default_value=P['coat_r'];bs.inputs['IOR'].default_value=1.5
    ma.pass_index=10;return ma
def apply():
    old=bpy.data.materials['Ernest_dark_wood_study'];ma=build();n=0
    for name in TARGETS:
        for s in bpy.data.objects[name].material_slots:
            if s.material==old:s.material=ma;n+=1
    return {'material':ma.name,'slots_replaced':n,'params':P}
