"""Composite physically rendered RGBA over the original photo, without regenerating it."""
from pathlib import Path
import sys,json,zlib
import cv2,numpy as np,OpenEXR
from photo_common_Z3 import floor_mask,shadow_receiver_mask
R=Path(__file__).resolve().parent;O=R/'out_Z6'
shot=sys.argv[1] if len(sys.argv)>1 else 'u1';mode=sys.argv[2] if len(sys.argv)>2 else 'preview'
fg=cv2.imread(str(O/f'{shot}_{mode}_foreground.png'),cv2.IMREAD_UNCHANGED).astype(np.float32)/65535
photo=cv2.imread(str(R/f'images/photos_srgb/{shot}.png')).astype(np.float32)/255
H,W=fg.shape[:2]
photo=cv2.resize(photo,(W,H),interpolation=cv2.INTER_AREA)
yy,xx=np.mgrid[:H,:W].astype('float32');rad=np.clip(((xx-W/2)/(W*.65))**2+((yy-H/2)/(H*.65))**2,0,1)[:,:,None]
a=fg[:,:,3:4];prem=fg[:,:,:3]*a
softness=.35+.45*rad
ap=cv2.GaussianBlur(a,(0,0),.65)[:,:,None];pp=cv2.GaussianBlur(prem,(0,0),.65)
a=a*(1-softness)+ap*softness;prem=prem*(1-softness)+pp*softness
fg[:,:,:3]=np.divide(prem,a,out=np.zeros_like(prem),where=a>1e-6);fg[:,:,3]=a[:,:,0]
alpha=np.clip(a,0,1)
del yy,xx,rad,prem,softness,ap,pp,a
def lin(v):return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
def srgb(v):return np.where(v<=.0031308,v*12.92,1.055*np.maximum(v,0)**(1/2.4)-.055)
catcher=np.ones_like(photo)
ef=O/f'{shot}_{mode}_passes0001.exr'
if ef.exists():
 sc=OpenEXR.File(str(ef)).channels()['Shadow Catcher'].pixels[:,:,:3].astype('float32')[:,:,::-1]
 catcher=np.clip(np.nan_to_num(sc,nan=1,posinf=4,neginf=0),0,4)
 del sc
basefile=O/f'{shot}_background_passes0001.exr'
if basefile.exists():
 base=OpenEXR.File(str(basefile)).channels()['Shadow Catcher'].pixels[:,:,:3].astype('float32')[:,:,::-1]
 base=cv2.resize(base,(W,H),interpolation=cv2.INTER_LINEAR);catcher=np.divide(catcher,base,out=np.ones_like(catcher),where=base>=.05)
 del base
catcher=1+(np.clip(catcher,0,4)-1)*shadow_receiver_mask(shot,W,H)[:,:,None]
mask=((alpha[:,:,0]>0)|(np.max(np.abs(catcher-1),axis=2)>.015)).astype('uint8')*255
cv2.imwrite(str(O/f'{shot}_effect_mask.png'),mask)
rgb=lin(fg[:,:,:3])*alpha+lin(photo)*catcher*(1-alpha)
# Separate existing reflected light from diffuse floor response before applying shadows.
# The unit-white pass removes Fresnel weighting from the furniture coverage mask.
def load_reflection(kind):
 path=O/f'{shot}_{mode}_floor_reflection_{kind}_passes0001.exr'
 v=OpenEXR.File(str(path)).channels()['Image'].pixels[:,:,:3].astype('float32')[:,:,::-1]
 # Radiance/coverage are nonnegative physical quantities. Cubic interpolation
 # overshoots at dark edges; dividing those lobes by tiny opacity made coloured
 # ringing in the floor. Linear interpolation preserves their valid range.
 v=np.maximum(np.nan_to_num(v,nan=0,posinf=0,neginf=0),0)
 return cv2.resize(v,(W,H),interpolation=cv2.INTER_LINEAR) if v.shape[:2]!=(H,W) else v
rcolor=O/f'{shot}_{mode}_floor_reflection_furniture_passes0001.exr'
if rcolor.exists():
 refl=load_reflection('furniture');opacity=load_reflection('opacity').mean(2,keepdims=True)
 white=load_reflection('white_reference').mean(2,keepdims=True)
 env=load_reflection('environment')*2**(-1.5)
 opacity=np.clip(np.nan_to_num(opacity,nan=0),0,1)
 coverage=np.clip(np.divide(opacity,white,out=np.zeros_like(opacity),where=white>1e-5),0,1)
 refl=np.nan_to_num(refl,nan=0,posinf=0,neginf=0)*2**(-1.5)
 unprem=np.divide(np.maximum(refl,0),opacity,out=np.zeros_like(refl),where=opacity>1e-5)
 display=cv2.imread(str(O/f'{shot}_{mode}_reflection_unprem_agx.png'),cv2.IMREAD_UNCHANGED)[:,:,:3].astype('float32')/65535
 if display.shape[:2]!=(H,W):display=cv2.resize(display,(W,H),interpolation=cv2.INTER_LINEAR)
 refl=lin(display)*opacity
 fm=floor_mask(shot,W,H)[:,:,None]
 # Robust photometric fit to the empty-floor photograph, using structural reflection
 # contrast while suppressing high-frequency timber grain and broad illumination gradients.
 ww=min(900,W);hh=max(1,round(H*ww/W));ps=cv2.resize(lin(photo),(ww,hh),interpolation=cv2.INTER_AREA)
 es=cv2.resize(np.maximum(env,0),(ww,hh),interpolation=cv2.INTER_AREA)
 ms=cv2.resize(fm[:,:,0],(ww,hh),interpolation=cv2.INTER_AREA)>.95
 lum=np.array([.0722,.7152,.2126],dtype='float32')
 pl=(cv2.GaussianBlur(ps,(0,0),1.0)@lum);el=(cv2.GaussianBlur(es,(0,0),1.0)@lum)
 ph=pl-cv2.GaussianBlur(pl,(0,0),16);eh=el-cv2.GaussianBlur(el,(0,0),16)
 valid=ms&(pl>.008)&(pl<.65)&(np.abs(eh)>1e-5)
 xx=eh[valid].astype('float64');yy=ph[valid].astype('float64')
 corr=float(np.corrcoef(xx,yy)[0,1]) if len(xx)>200 and xx.std()>1e-8 and yy.std()>1e-8 else 0.
 gain=float(np.dot(xx,yy)/max(np.dot(xx,xx),1e-12)) if len(xx) else 0.
 if corr>.12 and gain>0:
  for it in range(4):
   rr=yy-gain*xx;sig=max(float(np.median(np.abs(rr)))*1.4826,1e-5);weights=np.minimum(1,1.5*sig/np.maximum(np.abs(rr),1e-8));gain=float(np.sum(weights*xx*yy)/max(np.sum(weights*xx*xx),1e-12))
  gain=float(np.clip(gain,.1,120));existing_reflection=np.minimum(np.maximum(env*gain,0),lin(photo)*.90);fitmethod='robust photographic reflection-contrast fit'
 else:
  # Do not subtract misregistered synthetic window patterns when the fit is weak.
  # Conservative intrinsic estimate retains the observed floor colour and texture.
  # Use the SAME BRDF-derived intrinsic prior as the calibrated branch below.
  # The old fallback jumped from a0.72 to0.78 specular fraction merely when
  # correlation crossed0.12, darkening the floor after a camera refit even if
  # reflected furniture became brighter. No local image masks or painting.
  frac=np.clip(white*3.0,.18,.72);existing_reflection=lin(photo)*frac;fitmethod='BRDF-derived intrinsic prior consistent with calibrated-branch minimum; environment fit weak'
 existing_reflection=np.maximum(existing_reflection,lin(photo)*np.clip(white*3.0,.18,.72))
 existing_reflection=np.minimum(existing_reflection,lin(photo)*.90)*fm
 block=coverage;blockmethod='unweighted geometric coverage; conservative photo-based reflection estimate'
 if corr>.12 and gain>0 and (O/f'{shot}_{mode}_floor_reflection_environment_occluded_passes0001.exr').exists():
  env_occluded=load_reflection('environment_occluded')*2**(-1.5)
  env_lum=env@lum;loss_lum=np.maximum(env-env_occluded,0)@lum
  block=np.clip(np.divide(loss_lum,env_lum,out=np.zeros_like(env_lum),where=env_lum>1e-5),0,1)[:,:,None]
  # A ratio of two almost-black proxy reflections is numerically unstable. It
  # must not invent a furniture silhouette where no new-object reflection ray
  # exists. Use directional weighting only with actual coverage + reliable light.
  block*=np.minimum(coverage*8,1)*np.clip(env_lum[:,:,None]/.003,0,1)
  block=np.maximum(block,coverage)
  blockmethod='directional environment before/after opaque new-furniture occlusion; luminance-normalized radiance loss to preserve the photographed floor chroma'
 ao_path=O/f'{shot}_{mode}_contact_AO_passes0001.exr'
 if ao_path.exists():
  ao=OpenEXR.File(str(ao_path)).channels()['Image'].pixels[:,:,:3].astype('float32')[:,:,::-1]
  empty_path=O/f'{shot}_{mode}_contact_AO_empty_passes0001.exr'
  if empty_path.exists():
   empty=OpenEXR.File(str(empty_path)).channels()['Image'].pixels[:,:,:3].astype('float32')[:,:,::-1]
   ao=np.divide(ao,empty,out=np.ones_like(ao),where=empty>.05)
  ao=cv2.resize(ao,(W,H),interpolation=cv2.INTER_LINEAR)
  receiver=shadow_receiver_mask(shot,W,H)[:,:,None]
  catcher=np.minimum(catcher,1-(1-np.clip(ao,0,1))*.70*receiver)
  mask=np.maximum(mask,np.uint8((np.max(1-ao,axis=2)*receiver[:,:,0])>.001)*255)
 diffuse=np.maximum(lin(photo)-existing_reflection,0)
 background=diffuse*catcher+existing_reflection*(1-block*fm)+refl*fm
 rgb=lin(fg[:,:,:3])*alpha+background*(1-alpha)
 mask=np.maximum(mask,np.uint8((np.maximum(np.max(block,axis=2),coverage[:,:,0])*fm[:,:,0])>.001)*255);cv2.imwrite(str(O/f'{shot}_effect_mask.png'),mask)
 cv2.imwrite(str(O/f'{shot}_{mode}_reflection_coverage.png'),np.uint8(coverage[:,:,0]*fm[:,:,0]*255))
 (O/f'{shot}_{mode}_reflection_fit.json').write_text(json.dumps({'method':fitmethod,'environment_gain':gain,'contrast_correlation':corr,'existing_reflection_occlusion':blockmethod,'coverage':'opacity divided by unit-white BRDF response; existing reflection blocked by directional radiance loss where calibrated, otherwise geometric coverage, not double Fresnel','shadow':'diffuse component only; existing reflection retained outside occlusion','status':'photographic estimate, not measured HDR inverse rendering'},indent=2),encoding='utf8')
out=srgb(np.maximum(rgb,0))
# Match fine camera luminance grain on newly rendered surfaces only. The mixed
# second difference rejects ceiling gradients and estimates native JPEG-scale noise.
y0,y1=round(H*.08),round(H*.25);x0,x1=round(W*.15),round(W*.85)
patch=photo[y0:y1,x0:x1]@np.array([.0722,.7152,.2126],dtype='float32')
hp=.5*(patch[:-1,:-1]-patch[:-1,1:]-patch[1:,:-1]+patch[1:,1:])
sigma=float(np.clip(np.median(np.abs(hp-np.median(hp)))/.67448975,.65/255,1.25/255))
rng=np.random.default_rng(zlib.crc32(shot.encode()))
out+=rng.standard_normal((H,W),dtype=np.float32)[:,:,None]*(sigma*alpha)
(O/f'{shot}_{mode}_camera_grain.json').write_text(json.dumps({'luminance_sigma_8bit':sigma*255,'minimum_luminance_sigma_8bit':.65,'method':'robust mixed second-difference MAD with a 0.65/255 floor for JPEG-smoothed flat regions; applied to CG foreground only','optics':'premultiplied edge softening increases smoothly toward frame periphery','status':'photo-estimated camera texture, not sensor calibration'},indent=2))
out=np.clip(np.rint(out*255),0,255).astype('uint8')
cv2.imwrite(str(O/f'{shot}_{mode}_composite.jpg'),out,[cv2.IMWRITE_JPEG_QUALITY,98])
if mode=='full':cv2.imwrite(str(O/f'{shot}_full_composite.png'),out,[cv2.IMWRITE_PNG_COMPRESSION,6])
cv2.imwrite(str(O/f'{shot}_{mode}_alpha.png'),np.rint(alpha*255).astype('uint8'))
print('COMPOSITE_SAVED',shot,mode,W,H)
