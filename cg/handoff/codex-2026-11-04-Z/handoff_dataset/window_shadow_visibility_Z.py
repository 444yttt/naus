"""Test whether photo-derived profile shadows could affect the visible rug.
Diagnostic only: do not adopt schematic uniformly spaced window frames.
"""
from pathlib import Path
import bpy,json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parent;O=R/'out_Z';rows=[]
profiles=[(5.55,.06),(7.44,.02),(8.68,.04)]
for shot in ['p09','u1']:
    bpy.ops.wm.open_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();sun=s.objects['Sun_estimated_from_floor_shadows'];to_sun=-(sun.rotation_euler.to_matrix()@Vector((0,0,-1)));rug=next(o for o in s.objects if o.name.startswith('Shindo_'));count=0;lit=0;visible=[]
    def sun_clear(p):
        origin=p.copy();remaining=30.
        for _ in range(20):
            hit,loc,n,face,ob,ma=s.ray_cast(deps,origin,to_sun,distance=remaining)
            if not hit:return True
            dist=(loc-origin).length
            if not ob.hide_render and ob.visible_shadow:return False
            origin=loc+to_sun*.002;remaining-=dist+.002
        return False
    for v in rug.data.vertices:
        p=rug.matrix_world@v.co;p.z+=.002
        if to_sun.y>=0:continue
        t=-p.y/to_sun.y;cross=p+to_sun*t
        if not 0<cross.z<2.486:continue
        if not any(abs(cross.x-x)<width/2 for x,width in profiles):continue
        count+=1
        if not sun_clear(p):continue
        lit+=1;q=world_to_camera_view(s,s.camera,p)
        if q.z<=0 or not 0<q.x<1 or not 0<q.y<1:continue
        d=p-s.camera.location;hit,loc,n,face,ob,ma=s.ray_cast(deps,s.camera.location,d.normalized(),distance=d.length+.03)
        if hit and ob==rug and abs((loc-s.camera.location).length-d.length)<.025:
            visible.append({'world':list(p),'pixel':[q.x*s.render.resolution_x,(1-q.y)*s.render.resolution_y]})
    rows.append({'shot':shot,'rug_vertices_sampled':len(rug.data.vertices),'potential_profile_plane_intersections':count,'currently_sun_lit_intersections':lit,'visible_sun_lit_intersections':len(visible),'visible_samples':visible,'profile_candidates_world_x_and_width_m':profiles,'status':'photo-derived candidates, not production adopted; shadow-ray test skips invisible-shadow photo cards'})
(O/'window_shadow_visibility.json').write_text(json.dumps(rows,indent=2));print('PROFILE_SHADOW_VISIBILITY',[(r['shot'],r['potential_profile_plane_intersections'],r['currently_sun_lit_intersections'],r['visible_sun_lit_intersections']) for r in rows],flush=True)
