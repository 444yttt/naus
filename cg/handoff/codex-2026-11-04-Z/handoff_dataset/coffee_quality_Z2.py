"""Front Ernest tops only; exclude the integrated rear table sharing material10."""
from pathlib import Path
import json,cv2,numpy as np,OpenEXR
from PIL import Image
R=Path(__file__).resolve().parent;O=R/'out_Z2';rows=[]
def linear(v):
    v=v.astype('float32')/255;return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
for shot in json.loads((O/'native_progress.json').read_text())['completed']:
    ch=OpenEXR.File(str(O/f'{shot}_full_passes0001.exr')).channels();ids=ch['IndexMA.V'].pixels[::2,::2].copy();nz=ch['Normal.Z'].pixels[::2,::2].copy();x=ch['Position.X'].pixels[::2,::2].copy();y=ch['Position.Y'].pixels[::2,::2].copy();del ch
    mask=(abs(ids-10)<.01)&(nz>.9)&(x>7.2)&(x<8.35)&(y>1.59)&(y<3.41);mask=cv2.erode(mask.astype('uint8'),np.ones((5,5),'uint8'))>0
    if mask.sum()<100:
        rows.append({'shot':shot,'pixels':int(mask.sum()),'status':'front tops not sufficiently visible, no quality assertion'});continue
    versions={}
    for version,folder in [('W',R/'out/photo_final_W'),('X',R/'out_X'),('Z',R/'out_Z'),('Z2',O)]:
        if not (folder/f'{shot}_full_composite.png').exists():versions[version]=None;continue
        # Furniture and these cameras are invariant in views where the tops show.
        rgb=cv2.imread(str(folder/f'{shot}_full_composite.png'))[::2,::2,::-1];lum=linear(rgb)[mask]@np.array([.2126,.7152,.0722]);versions[version]={'linear_Y_p05_p50_p95':np.percentile(lum,[5,50,95]).tolist(),'linear_Y_std':float(lum.std()),'channel_clip_fraction':float((rgb[mask]>=254).mean())}
    rows.append({'shot':shot,'pixels':int(mask.sum()),'front_top_world_bbox_xy':[7.2,1.59,8.35,3.41],'versions':versions,'scope':'surface radiance gradients and clipping, not a measurement of lumens or an automatic aesthetic score; normal/material/world-position masks exclude rear sofa table'})
    if shot=='p09':
        im=Image.open(O/'p09_full_composite.png');im.crop((850,2650,2050,3550)).save(O/'p09_native_rug_coffee_crop.png')
(O/'coffee_quality.json').write_text(json.dumps(rows,indent=2));print('Z2_FRONT_COFFEE_MEASUREMENTS',rows,flush=True)
