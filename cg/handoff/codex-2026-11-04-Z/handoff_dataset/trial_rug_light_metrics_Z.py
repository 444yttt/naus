from pathlib import Path
import cv2,numpy as np,OpenEXR,json,sys
R=Path(__file__).resolve().parent;O=R/'out_Z';D=O/'light_trials';ch=OpenEXR.File(str(O/'p09_full_passes0001.exr')).channels();norm=np.stack([ch['Normal.'+a].pixels for a in 'XYZ'],2);ids=ch['IndexMA.V'].pixels.copy();del ch
rows=[]
def linear(v):return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
prefix=sys.argv[1] if len(sys.argv)>1 else 'sky'
for energy in (['3000_0.35','5000_0.35'] if prefix=='strong' else ['2000_0.35','300_0','1000_0','2000_0'] if prefix=='balance' else [200,400,800] if prefix=='upper' else [300,600,1000]):
    stem=prefix+'_' if prefix in ['balance','strong'] else prefix
    p=D/f'p09_{stem}{energy}.png'
    if not p.exists():continue
    raw=cv2.imread(str(p),-1);h,w=raw.shape[:2];rgb=linear(raw[:,:,:3][:,:,::-1].astype('float32')/65535);n=cv2.resize(norm,(w,h),interpolation=cv2.INTER_NEAREST);ix=cv2.resize(ids,(w,h),interpolation=cv2.INTER_NEAREST);base=(cv2.erode(np.uint8(abs(ix-8)<.01),np.ones((3,3),'uint8'))>0)&(raw[:,:,3]>65000);faces=[]
    for axis in range(3):
        for sign in [-1,1]:
            mask=base&(n[:,:,axis]*sign>.9)
            if mask.sum()<12:continue
            v=rgb[mask].mean(0);faces.append({'axis':axis,'sign':sign,'pixels':int(mask.sum()),'RGB':v.tolist(),'Y':float(v@np.array([.2126,.7152,.0722]))})
    rows.append({'energy':energy,'face_std_Y':float(np.std([f['Y'] for f in faces])),'faces':faces,'scope':'25% foreground lighting trial, matched masks; final native acceptance must be repeated'})
(D/f'{prefix}_metrics.json').write_text(json.dumps(rows,indent=2));print('LIGHT_TRIAL_METRICS',[(r['energy'],r['face_std_Y']) for r in rows],flush=True)
