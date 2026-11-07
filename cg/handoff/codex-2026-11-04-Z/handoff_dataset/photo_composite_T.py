"""Composite physically rendered RGBA over the original photo, without regenerating it."""
from pathlib import Path
import sys,json
import cv2,numpy as np,OpenEXR
from photo_common_S import floor_mask
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_T'
shot=sys.argv[1] if len(sys.argv)>1 else 'u1';mode=sys.argv[2] if len(sys.argv)>2 else 'preview'
fg=cv2.imread(str(O/f'{shot}_{mode}_foreground.png'),cv2.IMREAD_UNCHANGED).astype(np.float32)/65535
photo=cv2.imread(str(R/f'images/photos/{shot}.jpg')).astype(np.float32)/255
H,W=fg.shape[:2]
photo=cv2.resize(photo,(W,H),interpolation=cv2.INTER_AREA)
alpha=np.clip(fg[:,:,3:4],0,1)
def lin(v):return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
def srgb(v):return np.where(v<=.0031308,v*12.92,1.055*np.maximum(v,0)**(1/2.4)-.055)
catcher=np.ones_like(photo)
ef=O/f'{shot}_preview_passes0001.exr'
if ef.exists():
 sc=OpenEXR.File(str(ef)).channels()['Shadow Catcher'].pixels[:,:,:3].astype('float32')[:,:,::-1]
 catcher=np.clip(np.nan_to_num(sc,nan=1,posinf=4,neginf=0),0,4)
basefile=O/f'{shot}_background_passes0001.exr'
if basefile.exists():
 base=OpenEXR.File(str(basefile)).channels()['Shadow Catcher'].pixels[:,:,:3].astype('float32')[:,:,::-1]
 base=cv2.resize(base,(W,H),interpolation=cv2.INTER_LINEAR);catcher=np.divide(catcher,base,out=np.ones_like(catcher),where=base>=.05)
catcher=1+(np.clip(catcher,0,4)-1)*floor_mask(shot,W,H)[:,:,None]
mask=((alpha[:,:,0]>0)|(np.max(np.abs(catcher-1),axis=2)>.015)).astype('uint8')*255
cv2.imwrite(str(O/f'{shot}_effect_mask.png'),mask)
rgb=lin(fg[:,:,:3])*alpha+lin(photo)*catcher*(1-alpha)
# Full-frame new-furniture reflection. Physical dielectric response supplies opacity;
# static proxy reflections are excluded, and the photo supplies the original environment.
rcolor=O/f'{shot}_floor_reflection_furniture_passes0001.exr';rmatte=O/f'{shot}_floor_reflection_opacity_passes0001.exr'
if rcolor.exists() and rmatte.exists():
 refl=OpenEXR.File(str(rcolor)).channels()['Image'].pixels[:,:,:3].astype('float32')[:,:,::-1]
 matte=OpenEXR.File(str(rmatte)).channels()['Image'].pixels[:,:,:3].astype('float32')[:,:,::-1].mean(2,keepdims=True)
 assert refl.shape==rgb.shape and matte.shape[:2]==rgb.shape[:2]
 refl=np.nan_to_num(refl,nan=0,posinf=0,neginf=0)*2**(-1.5)
 matte=np.clip(np.nan_to_num(matte,nan=0),0,1)
 fmask=floor_mask(shot,W,H)[:,:,None]*(1-alpha)
 rgb=rgb*(1-matte*fmask)+refl*fmask
 mask=np.maximum(mask,np.uint8(matte[:,:,0]>.001)*255);cv2.imwrite(str(O/f'{shot}_effect_mask.png'),mask)
 cv2.imwrite(str(O/f'{shot}_reflection_opacity.png'),np.uint8(matte[:,:,0]*255))
out=srgb(np.maximum(rgb,0))
out=np.clip(np.rint(out*255),0,255).astype('uint8')
cv2.imwrite(str(O/f'{shot}_{mode}_composite.jpg'),out,[cv2.IMWRITE_JPEG_QUALITY,97])
cv2.imwrite(str(O/f'{shot}_{mode}_alpha.png'),np.rint(alpha*255).astype('uint8'))
print('COMPOSITE_SAVED',shot,mode,W,H)
