from pathlib import Path
import bpy
R=Path(__file__).resolve().parent;O=R/'out_Y';bpy.ops.wm.open_mainfile(filepath=str(R/'out_X/u2_photo_scene.blend'));S=bpy.context.scene
im=bpy.data.images.load(str(O/'u2_reflection_unprem.exr'));im.colorspace_settings.name='Linear Rec.709'
S.render.image_settings.file_format='PNG';S.render.image_settings.color_depth='16';S.render.image_settings.color_mode='RGBA'
im.save_render(str(O/'u2_reflection_unprem_agx.png'),scene=S)
print('DISPLAY_TRANSFORM',S.view_settings.view_transform,S.view_settings.look,S.view_settings.exposure,S.view_settings.gamma,flush=True)
