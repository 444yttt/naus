import bpy,sys
exec(open('/work/trial/calib_render.py').read().split("S.render.filepath=out")[0])
mode=sys.argv[sys.argv.index('--')+2]
for o in S.objects:
    if o.type=='LIGHT':
        if mode=='sun':o.data.energy=o.data.energy if o.name=='Sun_estimated_from_floor_shadows' else 0
        else:o.data.energy=0 if o.name=='Sun_estimated_from_floor_shadows' else o.data.energy
if mode=='sun':S.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
S.render.filepath=out;bpy.ops.render.render(write_still=True);print('CALIB_DONE',out)
