from pathlib import Path
import json,cv2,numpy as np,OpenEXR,hashlib
R=Path(__file__).resolve().parent;O=R/'out_Y';W=R/'out/photo_final_W';shots=['u1','u2','p09','p01','p13'];rows=[]
def image(p):return cv2.imread(str(p),cv2.IMREAD_COLOR)[:,:,::-1]
def linear(v):
 v=v.astype('float32')/255;return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
def luminance(v):return linear(v)@np.array([.2126,.7152,.0722],dtype='float32')
def cct(rgb):
 xyz=np.array([[.4124564,.3575761,.1804375],[.2126729,.7151522,.0721750],[.0193339,.1191920,.9503041]])@rgb;x,y=xyz[:2]/max(xyz.sum(),1e-9);n=(x-.3320)/(y-.1858);return float(-449*n**3+3525*n**2-6823.3*n+5520.33)
def project(c,p):
 p=np.array(p);q=(p-np.array(c['C']))@np.array(c['R']).T;return q[:,:2]/q[:,2:]*c['f']+c.get('principal_point_native_px',[c['W']/2,c['H']/2])
def wood_stats(im,c):
 # Screen bounds follow the SAME preserved world geometry in each camera.
 world=[[x,y,z] for x in [1.72,2.14] for y in [1.52,2.18] for z in [.27,.90]];uv=project(c,world);h,w=im.shape[:2];a=np.maximum(np.floor(uv.min(0)).astype(int),0);b=np.minimum(np.ceil(uv.max(0)).astype(int),[w,h]);crop=im[a[1]:b[1],a[0]:b[0]];rgb=crop.astype('float32');mask=(rgb[:,:,0]>rgb[:,:,1]*1.1)&(rgb[:,:,1]>rgb[:,:,2]*1.05)&(rgb[:,:,0]>8)&(rgb.max(2)<190);mask=cv2.erode(mask.astype('uint8'),np.ones((5,5),'uint8'))>0;values=luminance(crop)[mask]
 return {'sample_pixels':int(len(values)),'mean_Y':float(values.mean()),'min_Y':float(values.min()),'max_Y':float(values.max()),'max_min_ratio':float(values.max()/max(values.min(),1e-6)),'p95_p05_ratio':float(np.percentile(values,95)/max(np.percentile(values,5),1e-6)),'bbox':[a.tolist(),b.tolist()],'selection':'projected preserved wood-shell bounds, eroded brown-chroma pixels; camera-specific masks; luminance linear-sRGB, not illuminance'}
for shot in shots:
 old=image(W/f'{shot}_full_composite.png');new=image(O/f'{shot}_full_composite.png');photo=image(R/f'images/photos_srgb/{shot}.png');effect=cv2.imread(str(O/f'{shot}_effect_mask.png'),0);diff=cv2.absdiff(new,photo);unmodified=effect==0
 row={'shot':shot,'native_dimensions':[new.shape[1],new.shape[0]],'unchanged_plate_pixel_count':int(unmodified.sum()),'unchanged_plate_max_error_8bit':int(diff[unmodified].max()) if unmodified.any() else None}
 row['unchanged_plate_pass']=row['unchanged_plate_max_error_8bit'] is not None and row['unchanged_plate_max_error_8bit']<=2
 grain=json.loads((O/f'{shot}_full_camera_grain.json').read_text());wg=json.loads((W/f'{shot}_full_camera_grain.json').read_text());row['grain_identical']=grain==wg;row['grain']=grain
 if shot in ['u1','p09']:
  channels=OpenEXR.File(str(O/f'{shot}_full_passes0001.exr')).channels();norm=np.stack([channels['Normal.'+axis].pixels[::2,::2] for axis in 'XYZ'],axis=2);index=channels.get('IndexMA.V',channels.get('IndexOB.V')).pixels[::2,::2].astype('float32');index=index[:,:,0] if index.ndim==3 else index
  base=(np.abs(index-8)<.01).astype('uint8');base=cv2.erode(base,np.ones((5,5),'uint8'))>0;face=[];a=old[::2,::2];b=new[::2,::2];luma=luminance(a);lumb=luminance(b)
  for axis in range(3):
   for sign in [-1,1]:
    mask=base&(norm[:,:,axis]*sign>.90)
    if mask.sum()<250:continue
    ma=linear(a)[mask].mean(0);mb=linear(b)[mask].mean(0)
    face.append({'world_axis':axis,'sign':sign,'samples':int(mask.sum()),'W_mean_Y':float(luma[mask].mean()),'Y_mean_Y':float(lumb[mask].mean()),'W_mean_RGB_linear':ma.tolist(),'Y_mean_RGB_linear':mb.tolist(),'Y_red_blue_ratio':float(mb[0]/max(mb[2],1e-6)),'W_red_blue_ratio':float(ma[0]/max(ma[2],1e-6)),'Y_green_excess_over_RB':float(mb[1]-(mb[0]+mb[2])/2),'W_green_excess_over_RB':float(ma[1]-(ma[0]+ma[2])/2)})
  for f in face:f['W_CCT_proxy_K']=cct(f['W_mean_RGB_linear']);f['Y_CCT_proxy_K']=cct(f['Y_mean_RGB_linear'])
  sdw=float(np.std([v['W_mean_Y'] for v in face]));sdx=float(np.std([v['Y_mean_Y'] for v in face]));row['sofa']={'face_groups':face,'W_std_face_mean_Y':sdw,'Y_std_face_mean_Y':sdx,'contrast_increase_pass':len(face)>=2 and sdx>sdw,'method':'eroded material-index8 upholstery, world-normal component >0.90, native pixel stride2, same camera and geometry. RGB ratios and McCamy CCT derived from reflected upholstery colour are descriptive colour proxies, not measured illuminant CCT.'}
  del channels,norm,index
 if shot=='u2':
  row['eames_back']={'W':wood_stats(old,json.loads((W/'u2_camera.json').read_text())),'Y':wood_stats(new,json.loads((O/'u2_camera.json').read_text()))}
  h,w=new.shape[:2];covw=cv2.imread(str(W/'u2_full_reflection_coverage.png'),0);covx=cv2.imread(str(O/'u2_full_reflection_coverage.png'),0);aa=cv2.imread(str(O/'u2_full_alpha.png'),0);zone=np.zeros((h,w),'uint8');zone[int(h*.60):int(h*.82),int(w*.09):int(w*.30)]=1;mask=(zone>0)&(covx>55)&(covw>55)&(aa<2)
  ref=np.zeros((h,w),'uint8');ref[int(h*.67):int(h*.81),int(w*.09):int(w*.115)]=1;ref=(ref>0)&(aa<2);lp=luminance(photo);ref=ref&(lp<np.percentile(lp[ref],40))
  vals={k:float(luminance(im)[mask].mean()) for k,im in [('W',old),('Y',new),('photo_same_pixels',photo)]};vals.update(reference_photo_dark_reflection_band_Y=float(lp[ref].mean()),samples=int(mask.sum()),reference_samples=int(ref.sum()),region_normalized=[.09,.60,.30,.82],method='common rendered reflection coverage in Eames floor ROI excluding foreground. Reference is photographed dark window-reflection band, not an independently measured cast shadow.');row['eames_floor']=vals
 if shot=='p01':
  from photo_common_X import floor_mask
  fm=floor_mask(shot,new.shape[1],new.shape[0]);cov=cv2.imread(str(O/'p01_full_reflection_coverage.png'),0);alpha=cv2.imread(str(O/'p01_full_alpha.png'),0)
  # Independent far-floor ROI at lower left of the image. Exclude foreground,
  # reflection coverage and a100px dilation of them, not image colour difference.
  occupied=((cov>3)|(alpha>1)).astype('uint8');occupied=cv2.dilate(occupied,np.ones((101,101),'uint8'));h,w=fm.shape;roi=np.zeros_like(occupied);roi[int(h*.82):int(h*.98),int(w*.02):int(w*.25)]=1;far=(roi>0)&(occupied==0)&(fm>.99)
  close=(cov>55)&(alpha<2)&(fm>.99)
  means={k:im[far].mean(0).tolist() for k,im in [('photo',photo),('W',old),('Y',new)]};delta=np.array(means['Y'])-means['photo']
  row['floor_colour']={'far_ROI_normalized':[.02,.82,.25,.98],'sample_pixels':int(far.sum()),'mean_RGB_8bit':means,'Y_minus_photo_RGB_8bit':delta.tolist(),'far_mean_match_within_0_5':bool(np.max(np.abs(delta))<=.5),'near_reflection_pixels':int(close.sum()),'near_Y_photo_mean_abs_difference_8bit':float(diff[close].mean()) if close.any() else None,'Y_blue_excess_B_minus_R_delta':float(delta[2]-delta[0]),'note':'Fixed far-floor ROI excludes foreground and reflected geometry with101px dilation; rendered shadow/indirect-light influence is not excluded, so this ROI cannot independently establish absence of furniture influence. Full mean differences are retained rather than selecting pixels by image agreement. Actual source plate itself unchanged.'}
 scenes=json.loads((O/'scene_delta_Y.json').read_text());points=next(s for s in scenes if s['shot']==shot)['visible_island_joint_test_pixels']
 ao=OpenEXR.File(str(O/f'{shot}_full_contact_AO_passes0001.exr')).channels()['Image'].pixels[:,:,:3].astype('float32');empty=OpenEXR.File(str(O/f'{shot}_full_contact_AO_empty_passes0001.exr')).channels()['Image'].pixels[:,:,:3].astype('float32');rat=np.divide(ao,empty,out=np.ones_like(ao),where=empty>.05).mean(2);vals=[]
 for x,y in points:
  xx,yy=round(x*rat.shape[1]/new.shape[1]),round(y*rat.shape[0]/new.shape[0]);vals.append(float(rat[min(yy,rat.shape[0]-1),min(xx,rat.shape[1]-1)]))
 row['island_joint_AO']={'visible_sample_count':len(vals),'normalized_AO_values':vals,'minimum_ratio':min(vals) if vals else None,'shadow_present':min(vals)<.98 if vals else None,'visibility_note':'Island face samples immediately above tabletop, ray-tested against foreground geometry; null means seam samples are outside frame or occluded, not a failed pixel measurement.'}
 rows.append(row);print('METRICS',shot,flush=True)
(O/'metrics_Y.json').write_text(json.dumps(rows,indent=2))
