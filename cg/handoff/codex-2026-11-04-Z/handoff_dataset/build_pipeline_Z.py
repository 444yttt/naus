"""New rug revision; preserve X and the completed no-rug Y renders."""
from pathlib import Path
import shutil,json
R=Path(__file__).resolve().parent;O=R/'out_Z';O.mkdir(exist_ok=True)
for name in ['native_edge_camera_u2.json','native_edge_camera_p13.json']:
    shutil.copy2(R/'out_Y'/name,O/name)
src=(R/'prepare_Y.py').read_text(encoding='utf8').replace("O=R/'out_Y'","O=R/'out_Z'")
src=src.replace('ld.energy=300;ld.color=(.65,.82,1)','ld.energy=800;ld.color=(.65,.82,1)')
src=src.replace('c=json.loads(',"bpy.data.materials['Shedir02_Burro_colour_study'].node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.45\nc=json.loads(",1)
src=src.replace("bpy.ops.wm.save_as_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'))", "from add_rug_Z import add_rug\nadd_rug(S)\nbpy.ops.wm.save_as_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'))")
# Blender --python doesn't consistently put the source folder on sys.path.
src=src.replace("from add_rug_Z import", "sys.path.insert(0,str(R))\nfrom add_rug_Z import")
(R/'prepare_Z.py').write_text(src,encoding='utf8')
for name in ['render','photo_floor_reflection','photo_contact','photo_composite','transform_reflection','reflection_display_transform']:
    src=(R/f'{name}_Y.py').read_text(encoding='utf8').replace("O=R/'out_Y'","O=R/'out_Z'").replace('reflection_display_transform_Y.py','reflection_display_transform_Z.py')
    src=src.replace("'-b','--python'","'-b','--python-exit-code','1','--python'")
    (R/f'{name}_Z.py').write_text(src,encoding='utf8')
src=(R/'run_native_Y.py').read_text(encoding='utf8').replace("O=R/'out_Y'","O=R/'out_Z'")
for name in ['prepare','render','photo_floor_reflection','photo_contact','transform_reflection','photo_composite']:
    src=src.replace(f'{name}_Y.py',f'{name}_Z.py')
src=src.replace('Y_ALL_NATIVE_RENDERED','Z_ALL_NATIVE_RENDERED').replace('NATIVE_COMPLETE','Z_NATIVE_COMPLETE').replace("common lighting/layout'","common lighting/layout and restored common Shindo rug'")
(R/'run_native_Z.py').write_text(src,encoding='utf8')
print('Z_PIPELINE_PREPARED')
