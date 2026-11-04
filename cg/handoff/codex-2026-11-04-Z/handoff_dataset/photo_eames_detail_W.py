from pathlib import Path
import bpy,bmesh
R=Path(__file__).resolve().parent;O=R/'out/photo_final_W'
bpy.ops.wm.open_mainfile(filepath=str(O/'u2_photo_scene.blend'));S=bpy.context.scene
for ob in S.objects:
 if ob.name.startswith('SEAT-FABRIC'):
  ob.modifiers.clear();bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
  md=ob.modifiers.new('Close upholstery tessellation seams','REMESH');md.mode='VOXEL';md.voxel_size=.0035;md.use_smooth_shade=True
  sm=ob.modifiers.new('Finish repaired upholstery','SMOOTH');sm.factor=.55;sm.iterations=3
S.render.resolution_percentage=100;S.render.use_border=True;S.render.use_crop_to_border=True
S.render.border_min_x=0;S.render.border_max_x=.32;S.render.border_min_y=.20;S.render.border_max_y=.51
S.render.threads=4;S.cycles.samples=16;S.cycles.adaptive_min_samples=4;S.cycles.adaptive_threshold=.03
for n in list(S.node_tree.nodes):
 if n.type=='OUTPUT_FILE':S.node_tree.nodes.remove(n)
S.render.filepath=str(O/'u2_eames_native_detail.png');bpy.ops.render.render(write_still=True)
