from pathlib import Path
import cv2,numpy as np,OpenEXR,json
R=Path(__file__).resolve().parent;O=R/'out_Y';W=R/'out/photo_final_W';X=R/'out_X';results=[]
def lin(v):
 v=v.astype('float32')/255;return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
def cct(rgb):
 xyz=np.array([[.4124564,.3575761,.1804375],[.2126729,.7151522,.0721750],[.0193339,.1191920,.9503041]])@rgb;x,y=xyz[:2]/max(xyz.sum(),1e-9);q=(x-.332)/(y-.1858);return float(-449*q**3+3525*q*q-6823.3*q+5520.33)
lum=np.array([.2126,.7152,.0722],dtype='float32')
for shot in json.loads((O/'preview_progress.json').read_text())['completed']:
 new=cv2.imread(str(O/f'{shot}_preview_composite.jpg'))[:,:,::-1];h,w=new.shape[:2]
 def load(p):return cv2.resize(cv2.imread(str(p)),(w,h),interpolation=cv2.INTER_AREA)[:,:,::-1]
 old=load(W/f'{shot}_full_composite.png');ximg=load(X/f'{shot}_full_composite.png');photo=load(R/f'images/photos_srgb/{shot}.png');ch=OpenEXR.File(str(O/f'{shot}_preview_passes0001.exr')).channels();idx=ch.get('IndexMA.V',ch.get('IndexOB.V')).pixels;normal=np.stack([ch['Normal.'+a].pixels for a in 'XYZ'],2);pos=np.stack([ch['Position.'+a].pixels for a in 'XYZ'],2)
 row={'shot':shot,'status':'25% trial only, not native acceptance','dimensions':[w,h]}
 if shot in ['u1','p09']:
  base=cv2.erode((abs(idx-8)<.01).astype('uint8'),np.ones((3,3),'uint8'))>0;face=[]
  for axis in range(3):
   for sign in [-1,1]:
    m=base&(normal[:,:,axis]*sign>.9)
    if m.sum()<100:continue
    vals={name:lin(im)[m].mean(0) for name,im in [('W',old),('X',ximg),('Y',new)]}
    face.append({'axis':axis,'sign':sign,'pixels':int(m.sum()),**{name+'_RGB':v.tolist() for name,v in vals.items()},**{name+'_Y':float(v@lum) for name,v in vals.items()},'Y_CCT_proxy_K':cct(vals['Y']),'Y_green_excess':float(vals['Y'][1]-(vals['Y'][0]+vals['Y'][2])/2)})
  row['sofa']={'faces':face,'W_std':float(np.std([f['W_Y'] for f in face])),'X_std':float(np.std([f['X_Y'] for f in face])),'Y_std':float(np.std([f['Y_Y'] for f in face]))}
  spatial={}
  for name,m in [('window_end',base&(pos[:,:,1]<1.1)),('room_end',base&(pos[:,:,1]>3.6))]:
   if m.sum()>20:
    values={tag:lin(im)[m].mean(0) for tag,im in [('W',old),('X',ximg),('Y',new)]};spatial[name]={'pixels':int(m.sum()),**{tag+'_CCT_proxy_K':cct(v) for tag,v in values.items()}}
  row['spatial_colour_diagnostic']=spatial
 coffee=cv2.erode(((abs(idx-10)<.01)&(normal[:,:,2]>.9)).astype('uint8'),np.ones((3,3),'uint8'))>0
 if coffee.sum()>50:
  values=lin(new)[coffee]@lum;row['coffee_top']={'samples':int(coffee.sum()),'luminance_quantiles':np.percentile(values,[5,50,95]).tolist(),'luminance_std':float(values.std()),'clipped_RGB_fraction':float((new[coffee]>=253).any(1).mean())}
 cov=cv2.imread(str(O/f'{shot}_preview_reflection_coverage.png'),0);alpha=cv2.imread(str(O/f'{shot}_preview_alpha.png'),0)
 if shot=='u2':
  cw=cv2.resize(cv2.imread(str(W/'u2_full_reflection_coverage.png'),0),(w,h));zone=np.zeros((h,w),'uint8');zone[int(h*.60):int(h*.82),int(w*.09):int(w*.30)]=1;m=(zone>0)&(cov>55)&(cw>55)&(alpha<2)
  row['eames_broad_floor']={'pixels':int(m.sum()),**{tag:float((lin(im)[m]@lum).mean()) for tag,im in [('W',old),('X',ximg),('Y',new),('photo',photo)]},'note':'historical mixed shadow/reflection ROI retained; not an isolated cast-shadow measurement'}
 if shot=='p01':
  from photo_common_X import floor_mask
  occupied=cv2.dilate(np.uint8((cov>3)|(alpha>1)),np.ones((25,25),'uint8'));roi=np.zeros((h,w),'uint8');roi[int(h*.82):int(h*.98),int(w*.02):int(w*.25)]=1;m=(roi>0)&(occupied==0)&(floor_mask(shot,w,h)>.99)
  row['far_floor_fixed_ROI']={'pixels':int(m.sum()),'mean_RGB_difference_Y_minus_photo':(new[m].mean(0)-photo[m].mean(0)).tolist(),'note':'original geometric ROI retained; indirect-light effects may extend into it'}
 row['reflection_colour_audit']=json.loads((O/f'{shot}_preview_reflection_colour_audit.json').read_text());results.append(row)
(O/'preview_metrics.json').write_text(json.dumps(results,indent=2));print(json.dumps([{k:v for k,v in r.items() if k not in ['sofa','reflection_colour_audit']} for r in results],indent=2))
