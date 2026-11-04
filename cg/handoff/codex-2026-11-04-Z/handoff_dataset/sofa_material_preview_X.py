from pathlib import Path
import bpy,sys,json
R=Path(__file__).resolve().parent;O=R/'out_X';bpy.ops.wm.open_mainfile(filepath=str(O/'p09_photo_scene.blend'));S=bpy.context.scene
bs=bpy.data.materials['Shedir02_Burro_colour_study'].node_tree.nodes.get('Principled BSDF')
S.render.resolution_percentage=25;S.cycles.samples=24;S.render.threads=6
for label,rough,coat,cr,dr in [('coat30',.38,.30,.25,0.),('rough_diffuse',.46,.20,.28,.35)]:
 bs.inputs['Roughness'].default_value=rough;bs.inputs['Coat Weight'].default_value=coat;bs.inputs['Coat Roughness'].default_value=cr;bs.inputs['Diffuse Roughness'].default_value=dr
 S.render.filepath=str(O/f'previews/p09_{label}.png')
 for nd in S.node_tree.nodes:
  if nd.type=='OUTPUT_FILE':nd.base_path=str(O/f'previews/p09_{label}_passes')
 bpy.ops.render.render(write_still=True)
print('MATERIAL_PREVIEWS_READY')
