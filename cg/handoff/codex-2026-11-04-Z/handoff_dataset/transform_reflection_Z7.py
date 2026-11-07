from pathlib import Path
import OpenEXR,numpy as np,subprocess,sys,json
R=Path(__file__).resolve().parent;O=R/'out_Z7';shot=sys.argv[1];mode=sys.argv[2]
f=OpenEXR.File(str(O/f'{shot}_{mode}_floor_reflection_furniture_passes0001.exr')).channels()['Image'].pixels[:,:,:3].astype('float32')
a=OpenEXR.File(str(O/f'{shot}_{mode}_floor_reflection_opacity_passes0001.exr')).channels()['Image'].pixels[:,:,:3].astype('float32').mean(2,keepdims=True)
u=np.divide(np.maximum(f,0),a,out=np.zeros_like(f),where=a>1e-5)
OpenEXR.File({}, {'RGB':u}).write(str(O/f'{shot}_{mode}_reflection_unprem.exr'))
with (O/f'{shot}_{mode}_reflection_display.log').open('w') as log:subprocess.run([str(R/'runtime/blender-4.5.9-windows-x64/blender.exe'),'-b','--python-exit-code','1','--python',str(R/'reflection_display_transform_Z7.py'),'--',shot,mode],stdout=log,stderr=subprocess.STDOUT,check=True)
outside=a[:,:,0]<1e-5
stats={'uncovered_raw_mean_RGB':f[outside].mean(0).tolist(),'uncovered_raw_p99_RGB':np.percentile(f[outside],99,axis=0).tolist(),'view_transform':'same source-scene AgX, Medium High Contrast, exposure -1.5; unpremultiplied reflected furniture radiance transformed before BRDF weighting','old_method':'Reinhard tone curve, inconsistent with foreground AgX','photo_edited':False}
(O/f'{shot}_{mode}_reflection_colour_audit.json').write_text(json.dumps(stats,indent=2))
