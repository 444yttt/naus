from pathlib import Path
R=Path(__file__).resolve().parent
exec(compile((R/'metrics_X.py').read_text().split('for shot in shots:')[0],str(R/'metrics_X.py'),'exec'))
from photo_common_X import floor_mask
new=image(O/'p01_full_composite.png');old=image(W/'p01_full_composite.png');photo=image(R/'images/photos_srgb/p01.png');h,w=new.shape[:2];fm=floor_mask('p01',w,h);cov=cv2.imread(str(O/'p01_full_reflection_coverage.png'),0);alpha=cv2.imread(str(O/'p01_full_alpha.png'),0)
occupied=cv2.dilate(((cov>3)|(alpha>1)).astype('uint8'),np.ones((101,101),'uint8'));roi=np.zeros_like(occupied);roi[int(h*.82):int(h*.98),int(w*.02):int(w*.25)]=1;far=(roi>0)&(occupied==0)&(fm>.99);near=(cov>55)&(alpha<2)&(fm>.99)
d={'sample_pixels':int(far.sum()),'mean_RGB_8bit':{k:im[far].mean(0).tolist() for k,im in [('photo',photo),('W',old),('X',new)]},'near_reflection_pixels':int(near.sum()),'near_mean_abs_X_photo':float(cv2.absdiff(new,photo)[near].mean())};(O/'early_floor_p01.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
sc=OpenEXR.File(str(O/'p01_full_passes0001.exr')).channels()['Shadow Catcher'].pixels[:,:,:3].astype('float32');base=OpenEXR.File(str(O/'p01_background_passes0001.exr')).channels()['Shadow Catcher'].pixels[:,:,:3].astype('float32');base=cv2.resize(base,(w,h),interpolation=cv2.INTER_LINEAR);ratio=np.divide(sc,base,out=np.ones_like(sc),where=base>=.05)
physical=np.max(np.abs(ratio-1),2)>.005
ao=OpenEXR.File(str(O/'p01_full_contact_AO_passes0001.exr')).channels()['Image'].pixels[:,:,:3].astype('float32');empty=OpenEXR.File(str(O/'p01_full_contact_AO_empty_passes0001.exr')).channels()['Image'].pixels[:,:,:3].astype('float32');ar=np.divide(ao,empty,out=np.ones_like(ao),where=empty>.05);physical|=cv2.resize(np.max(np.abs(ar-1),2),(w,h),interpolation=cv2.INTER_LINEAR)>.005
occupied=cv2.dilate(((cov>1)|(alpha>1)|physical).astype('uint8'),np.ones((101,101),'uint8'));far2=(roi>0)&(occupied==0)&(fm>.99);print('PHYSICALLY_UNAFFECTED',int(far2.sum()),{k:im[far2].mean(0).tolist() for k,im in [('photo',photo),('X',new)]});cv2.imwrite(str(O/'previews/p01_unaffected_floor_mask.png'),np.uint8(far2)*255)
