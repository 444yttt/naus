from pathlib import Path
import cv2,numpy as np,OpenEXR,json
R=Path(__file__).resolve().parent;O=R/'out_Z2';rows=[]
def linear(v):return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
def cct(rgb):
 xyz=np.array([[.4124564,.3575761,.1804375],[.2126729,.7151522,.0721750],[.0193339,.1191920,.9503041]])@rgb;x,y=xyz[:2]/max(xyz.sum(),1e-9);q=(x-.332)/(y-.1858);return float(-449*q**3+3525*q*q-6823.3*q+5520.33)
for shot in ['u1','p09']:
 p=O/f'{shot}_full_foreground.png'
 if not p.exists():continue
 channels=OpenEXR.File(str(O/f'{shot}_full_passes0001.exr')).channels();norm=np.stack([channels['Normal.'+a].pixels[::2,::2] for a in 'XYZ'],2);idx=channels['IndexMA.V'].pixels[::2,::2].copy();del channels
 raw=cv2.imread(str(p),-1)[::2,::2];opaque=raw[:,:,3]>65000;rgb=raw[:,:,:3][:,:,::-1].astype('float32')/65535;rgb=linear(rgb);old=cv2.imread(str(R/f'out/photo_final_W/{shot}_full_composite.png'))[::2,::2,::-1].astype('float32')/255;old=linear(old);base=(cv2.erode(np.uint8(abs(idx-8)<.01),np.ones((5,5),'uint8'))>0)&opaque;face=[]
 for axis in range(3):
  for sign in [-1,1]:
   m=base&(norm[:,:,axis]*sign>.9)
   if m.sum()<250:continue
   a=old[m].mean(0);b=rgb[m].mean(0);face.append({'axis':axis,'sign':sign,'pixels':int(m.sum()),'W_RGB':a.tolist(),'Z_RGB':b.tolist(),'W_Y':float(a@np.array([.2126,.7152,.0722])),'Z_Y':float(b@np.array([.2126,.7152,.0722])),'Z_CCT_proxy_K':cct(b),'W_green_excess':float(a[1]-(a[0]+a[2])/2),'Z_green_excess':float(b[1]-(b[0]+b[2])/2)})
 rows.append({'shot':shot,'status':'native foreground before final camera grain, preliminary only','face_groups':face,'W_std':float(np.std([f['W_Y'] for f in face])),'Z_std':float(np.std([f['Z_Y'] for f in face]))})
faces=[f for r in rows for f in r['face_groups']];neg=[f['Z_CCT_proxy_K'] for f in faces if f['axis']==1 and f['sign']==-1];pos=[f['Z_CCT_proxy_K'] for f in faces if f['axis']==1 and f['sign']==1];result={'views':rows,'original_directional_colour_method':{'window_minus_Y_CCT_proxy_K':float(np.mean(neg)) if neg else None,'room_plus_Y_CCT_proxy_K':float(np.mean(pos)) if pos else None,'window_warmer':bool(neg and pos and np.mean(neg)<np.mean(pos)),'caveat':'reflected colour proxy, not measured illuminant CCT; normals include cushion-internal patches; position-based diagnostic retained separately'}};(O/'early_native_colour.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
