"""Use the exact native acceptance masks for lighting previews; report alias caveat."""
from pathlib import Path
import cv2,numpy as np,OpenEXR,json,sys
R=Path(__file__).resolve().parent;O=R/'out_Z';ch=OpenEXR.File(str(O/'p09_full_passes0001.exr')).channels();norm=np.stack([ch['Normal.'+a].pixels[::2,::2] for a in 'XYZ'],2);ids=ch['IndexMA.V'].pixels[::2,::2].copy();del ch
base=cv2.erode(np.uint8(abs(ids-8)<.01),np.ones((5,5),'uint8'))>0;masks=[]
for axis in range(3):
    for sign in [-1,1]:
        mask=base&(norm[:,:,axis]*sign>.9)
        if mask.sum()>=250:masks.append((axis,sign,mask))
def lin(v):return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
rows=[]
files=['p09_sky300.png','p09_balance_2000_0.35.png','p09_strong_3000_0.35.png','p09_strong_5000_0.35.png']
kind=sys.argv[1] if len(sys.argv)>1 else 'sky'
if kind=='material':files=[p.name for p in sorted((O/'light_trials').glob('p09_material_*.png'))]
if kind=='warm350':files=['p09_sheen45_warm350.png']
if kind=='sky800':files=['p09_sheen45_sky800.png']
for name in files:
    raw=cv2.imread(str(O/'light_trials'/name),-1);rgb=lin(raw[:,:,:3][:,:,::-1].astype('float32')/65535);rgb=cv2.resize(rgb,(ids.shape[1],ids.shape[0]),interpolation=cv2.INTER_LINEAR);faces=[]
    for axis,sign,m in masks:
        c=rgb[m].mean(0);faces.append({'axis':axis,'sign':sign,'RGB':c.tolist(),'Y':float(c@np.array([.2126,.7152,.0722])),'green_excess':float(c[1]-(c[0]+c[2])/2)})
    rows.append({'file':name,'face_std_Y':float(np.std([f['Y'] for f in faces])),'faces':faces,'method':'25% lighting render resampled to exact native acceptance masks, native stride2/erosion5; preview aliasing remains, not final acceptance'})
(O/f'light_trials/native_mask_{kind}_metrics.json').write_text(json.dumps(rows,indent=2));print('EXACT_NATIVE_MASK_TRIALS',[(r['file'],r['face_std_Y']) for r in rows],flush=True)
