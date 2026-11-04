from pathlib import Path
import OpenEXR,numpy as np,json
R=Path(__file__).resolve().parent;O=R/'out_Y';shot='u2'
f=OpenEXR.File(str(O/f'{shot}_preview_floor_reflection_furniture_passes0001.exr')).channels()['Image'].pixels[:,:,:3].astype('float32')
a=OpenEXR.File(str(O/f'{shot}_preview_floor_reflection_opacity_passes0001.exr')).channels()['Image'].pixels[:,:,:3].astype('float32').mean(2,keepdims=True)
u=np.divide(f,a,out=np.zeros_like(f),where=a>1e-5)
OpenEXR.File({}, {'RGB':u.astype('float32')}).write(str(O/f'{shot}_reflection_unprem.exr'))
(O/'reflection_uncovered_audit.json').write_text(json.dumps({'outside_coverage_radiance_mean_RGB':f[a[:,:,0]<1e-5].mean(0).tolist(),'outside_coverage_radiance_p99_RGB':np.percentile(f[a[:,:,0]<1e-5],99,axis=0).tolist(),'covered_radiance_mean_RGB':u[a[:,:,0]>.01].mean(0).tolist(),'status':'prototype with area lights visible to glossy rays; reject if outside coverage radiance is nonzero'},indent=2))
