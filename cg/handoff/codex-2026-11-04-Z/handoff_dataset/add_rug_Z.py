"""Common Shindo study, based on official finish/pile reference, not a factory mesh."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R/'out_Z'
def add_rug(S):
    x0,y0,x1,y1=5.2,.35,8.7,4.35
    # Keep furniture and cameras untouched. Thin flexible pile compresses beneath
    # the existing feet rather than lifting the five common furniture layouts.
    contacts=set()
    for ob in S.objects:
        if ob.type!='MESH' or ob.hide_render or not ob.visible_camera:continue
        if ob.name.startswith(('LDK_','TV_','Kitchen','Hall','Ceiling','Existing_','Balcony','Diagonal','Sink','Faucet')):continue
        for v in ob.data.vertices:
            p=ob.matrix_world@v.co
            if -.001<=p.z<=.006 and x0-.04<p.x<x1+.04 and y0-.04<p.y<y1+.04:
                contacts.add((round(p.x,2),round(p.y,2)))
    # A shallow compression pocket is enough for the documented 3-4mm pile.
    n,m=100,115;verts=[];faces=[]
    for j in range(m+1):
        y=y0+(y1-y0)*j/m
        for i in range(n+1):
            x=x0+(x1-x0)*i/n;d=min((math.hypot(x-a,y-b) for a,b in contacts),default=1)
            z=.00015+.00465*(1-math.exp(-((d/.028)**2)))
            edge=min(x-x0,x1-x,y-y0,y1-y);z=min(z,.0015+.0033*min(1,max(0,edge/.008)))
            verts.append((x,y,z))
    for j in range(m):
        for i in range(n):
            k=j*(n+1)+i;faces.append((k,k+1,k+n+2,k+n+1))
    mesh=bpy.data.meshes.new('Shindo_Natural_Z_mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new('Shindo_Natural_4000x3500_Z',mesh);S.collection.objects.link(ob);ob.pass_index=12
    uv=mesh.uv_layers.new(name='UVMap')
    for p in mesh.polygons:
        p.use_smooth=True
        for li in p.loop_indices:
            x,y,z=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=((x-x0)/(x1-x0),(y-y0)/(y1-y0))
    solid=ob.modifiers.new('Thin woven backing','SOLIDIFY');solid.thickness=.00012;solid.offset=-1
    ma=bpy.data.materials.new('Shindo_Natural_official_finish_Z');ma.use_nodes=True;ma.pass_index=12
    nn=ma.node_tree.nodes;ll=ma.node_tree.links;b=nn.get('Principled BSDF');b.inputs['Roughness'].default_value=.85;b.inputs['Sheen Weight'].default_value=.22;b.inputs['Sheen Roughness'].default_value=.6
    tex=nn.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(O/'Shindo_Natural_official_reference.jpg'),check_existing=True);tex.image.pack();ll.new(tex.outputs['Color'],b.inputs['Base Color'])
    tc=nn.new('ShaderNodeTexCoord');noise=nn.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1400;noise.inputs['Detail'].default_value=2;ll.new(tc.outputs['Object'],noise.inputs['Vector'])
    bump=nn.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.00018;ll.new(noise.outputs['Fac'],bump.inputs['Height']);ll.new(bump.outputs[0],b.inputs['Normal'])
    sep=nn.new('ShaderNodeSeparateXYZ');ll.new(tc.outputs['UV'],sep.inputs[0]);left=nn.new('ShaderNodeMath');left.operation='LESS_THAN';left.inputs[1].default_value=.15/(x1-x0);ll.new(sep.outputs['X'],left.inputs[0]);right=nn.new('ShaderNodeMath');right.operation='GREATER_THAN';right.inputs[1].default_value=1-.15/(x1-x0);ll.new(sep.outputs['X'],right.inputs[0]);edge=nn.new('ShaderNodeMath');edge.operation='MAXIMUM';ll.new(left.outputs[0],edge.inputs[0]);ll.new(right.outputs[0],edge.inputs[1])
    wave=nn.new('ShaderNodeTexWave');wave.bands_direction='Y';wave.inputs['Scale'].default_value=35;ll.new(tc.outputs['Object'],wave.inputs['Vector']);mask=nn.new('ShaderNodeMath');mask.operation='MULTIPLY';ll.new(edge.outputs[0],mask.inputs[0]);ll.new(wave.outputs['Fac'],mask.inputs[1]);rough=nn.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.85;rough.inputs['To Max'].default_value=.58;ll.new(mask.outputs[0],rough.inputs['Value']);ll.new(rough.outputs['Result'],b.inputs['Roughness'])
    ob.data.materials.append(ma)
    meta={'brand':'Poliform','model':'Shindo','colour':'Natural','rect':[x0,y0,x1,y1],'size_mm':[4000,3500],'size_status':'restored previously approved provisional layout; not a confirmed stock size','geometry_status':'dimensioned study mesh, not official manufacturer 3D','official_reference':'https://www.poliform.it/en/products/shindo/','finish_image_source':'https://s3.poliform.it/2025/07/Poliform_tappeti_SHINDO_finiture_1300x1740px_natural.jpg','pile_reference_mm':[3,4],'total_top_height_m':.0048,'border_optical_motif_width_m':.15,'contact_compression_points':len(contacts),'furniture_pose_changes':0,'existing_camera_changes':0,'purpose':'opaque rug occludes original floor and its existing reflected light; all new contact/reflection passes rerendered'}
    ob['source_status']=meta['geometry_status'];ob['layout_size_status']=meta['size_status']
    (O/'rug_specification.json').write_text(json.dumps(meta,indent=2));return ob
