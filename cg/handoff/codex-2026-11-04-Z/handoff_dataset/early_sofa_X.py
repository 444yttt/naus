from pathlib import Path
import cv2,numpy as np,OpenEXR,json,sys
R=Path(__file__).resolve().parent;O=R/'out_X';W=R/'out/photo_final_W';shot=sys.argv[1]
ch=OpenEXR.File(str(O/f'{shot}_full_passes0001.exr')).channels();n=np.stack([ch['Normal.'+a].pixels[::3,::3] for a in 'XYZ'],axis=2);idx=ch['IndexMA.V'].pixels[::3,::3];base=cv2.erode((abs(idx-8)<.01).astype('uint8'),np.ones((5,5),'uint8'))>0
old=cv2.imread(str(W/f'{shot}_full_composite.png'))[::3,::3,::-1];raw=cv2.imread(str(O/f'{shot}_full_foreground.png'),cv2.IMREAD_UNCHANGED)[::3,::3];new=raw[:,:,:3][:,:,::-1].astype('float32')/257;base&=raw[:,:,3]>65000
def lin(im):
 v=im.astype('float32')/255;return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
def lum(im):return lin(im)@np.array([.2126,.7152,.0722],dtype='float32')
a,b=lum(old),lum(new);rows=[]
for axis in range(3):
 for sign in [-1,1]:
  m=base&(n[:,:,axis]*sign>.9)
  if m.sum()>100:
   ar=lin(old)[m].mean(0);br=lin(new)[m].mean(0)
   rows.append({'axis':axis,'sign':sign,'count':int(m.sum()),'W_Y':float(a[m].mean()),'X_foreground_Y':float(b[m].mean()),'W_green_excess':float(ar[1]-(ar[0]+ar[2])/2),'X_green_excess':float(br[1]-(br[0]+br[2])/2)})
d={'shot':shot,'method':'early diagnostic on opaque foreground before final camera grain; stride3','faces':rows,'W_std':float(np.std([r['W_Y'] for r in rows])),'X_std':float(np.std([r['X_foreground_Y'] for r in rows]))};(O/f'early_sofa_{shot}.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
