from pathlib import Path
import cv2,numpy as np,OpenEXR,json
R=Path(__file__).resolve().parent;O=R/'out_Y';rows=[]
for label in ['moderate']:
 path=O/f'p09_{label}_foreground';raw=cv2.imread(str(path.with_suffix('.png')),cv2.IMREAD_UNCHANGED);h,w=raw.shape[:2];old=cv2.resize(cv2.imread(str(R/'out/photo_final_W/p09_full_composite.png')),(w,h),interpolation=cv2.INTER_AREA)[:,:,::-1];new=raw[:,:,:3][:,:,::-1].astype('float32')/257
 ch=OpenEXR.File(str(O/f'p09_{label}_passes0001.exr')).channels();n=np.stack([ch['Normal.'+a].pixels for a in 'XYZ'],axis=2);idx=ch['IndexMA.V'].pixels;mask=cv2.erode((abs(idx-8)<.01).astype('uint8'),np.ones((3,3),'uint8'))>0;mask&=raw[:,:,3]>65000
 def linear(im):
  v=im.astype('float32')/255;return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
 a=linear(old);b=linear(new);al=a@np.array([.2126,.7152,.0722],dtype='float32');bl=b@np.array([.2126,.7152,.0722],dtype='float32');faces=[]
 for axis in range(3):
  for sign in [-1,1]:
   m=mask&(n[:,:,axis]*sign>.9)
   if m.sum()<100:continue
   faces.append({'axis':axis,'sign':sign,'W_Y':float(al[m].mean()),'new_Y':float(bl[m].mean())})
 row={'variant':label,'faces':faces,'W_std':float(np.std([f['W_Y'] for f in faces])),'new_std':float(np.std([f['new_Y'] for f in faces]))};rows.append(row)
(O/'p09_moderate_metrics.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
