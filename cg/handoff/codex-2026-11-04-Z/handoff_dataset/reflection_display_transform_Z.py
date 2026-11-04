from pathlib import Path
import bpy,sys
R=Path(__file__).resolve().parent;O=R/'out_Z';shot,mode=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=str(O/f'{shot}_photo_scene.blend'));S=bpy.context.scene
im=bpy.data.images.load(str(O/f'{shot}_{mode}_reflection_unprem.exr'));im.colorspace_settings.name='Linear Rec.709';S.render.image_settings.file_format='PNG';S.render.image_settings.color_depth='16';S.render.image_settings.color_mode='RGBA'
im.save_render(str(O/f'{shot}_{mode}_reflection_unprem_agx.png'),scene=S)
print('AGX_REFLECTION',shot,mode,S.view_settings.view_transform,S.view_settings.look,S.view_settings.exposure,flush=True)
