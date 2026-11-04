from pathlib import Path
import sys,json,cv2,numpy as np,OpenEXR
from photo_common_S import floor_mask
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_S';shot=sys.argv[1];td=O/f'{shot}_tiles'
m=json.loads((td/'manifest.json').read_text());W,H=m['W'],m['H']
photo=cv2.imread(str(R/f'images/photos/{shot}.jpg'));assert photo.shape[:2]==(H,W);out=photo.copy()
floormask=floor_mask(shot,W,H)
basefile=O/f'{shot}_background_passes0001.exr';base=None
if basefile.exists():base=OpenEXR.File(str(basefile)).channels()['Shadow Catcher'].pixels[:,:,:3].astype('float32')[:,:,::-1]
fg=np.zeros((H,W,4),dtype='uint16')
accum=np.zeros((H,W,3),dtype='float32');weights=np.zeros((H,W),dtype='float32')
def lin(v):return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
def srgb(v):return np.where(v<=.0031308,v*12.92,1.055*np.maximum(v,0)**(1/2.4)-.055)
for t in m['tiles']:
 if t.get('blank'):continue
 a,b,aa,bb=t['padded'];x,y,x2,y2=t['core'];im=cv2.imread(str(td/t['file']),cv2.IMREAD_UNCHANGED)
 assert im is not None,t
 assert abs(im.shape[1]-(aa-a))<=1 and abs(im.shape[0]-(bb-b))<=1,(t,im.shape)
 # Blender's border coordinates can round by one pixel. Anchor top/left and pad
 # the final missing edge pixel, rather than rescaling calibrated geometry.
 if im.shape[:2]!=(bb-b,aa-a):im=cv2.copyMakeBorder(im,0,max(0,bb-b-im.shape[0]),0,max(0,aa-a-im.shape[1]),cv2.BORDER_REPLICATE)[:bb-b,:aa-a]
 core=np.zeros((y2-y,x2-x,4),dtype='uint16');ix=max(x,a);iy=max(y,b);ix2=min(x2,aa);iy2=min(y2,bb)
 if ix2>ix and iy2>iy:core[iy-y:iy2-y,ix-x:ix2-x]=im[iy-b:iy2-b,ix-a:ix2-a]
 fg[y:y2,x:x2]=core
 f=im.astype('float32')/65535;alpha=np.clip(f[:,:,3:4],0,1);p=photo[b:bb,a:aa].astype('float32')/255
 # Cycles' dedicated catcher pass contains coloured indirect light/reflections
 # beyond the Combined alpha. Multiply it over the linear photographic plate.
 catcher=np.ones((bb-b,aa-a,3),dtype='float32')
 ef=list(td.glob(Path(t['file']).stem+'_passes*.exr'))
 if ef:
  ch=OpenEXR.File(str(ef[0])).channels();sc=ch['Shadow Catcher'].pixels[:,:,:3].astype('float32')[:,:,::-1]
  if sc.shape[:2]!=catcher.shape[:2]:sc=cv2.copyMakeBorder(sc,0,max(0,bb-b-sc.shape[0]),0,max(0,aa-a-sc.shape[1]),cv2.BORDER_REPLICATE)[:bb-b,:aa-a]
  catcher[:]=sc
 catcher=np.clip(np.nan_to_num(catcher,nan=1,posinf=4,neginf=0),0,4)
 if base is not None:
  mx,my=np.meshgrid((np.arange(a,aa,dtype='float32')+.5)*base.shape[1]/W-.5,(np.arange(b,bb,dtype='float32')+.5)*base.shape[0]/H-.5)
  baseline=cv2.remap(base,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE);catcher=np.divide(catcher,baseline,out=np.ones_like(catcher),where=baseline>=.05)
 catcher=1+(np.clip(catcher,0,4)-1)*floormask[b:bb,a:aa,None]
 rgb=lin(f[:,:,:3])*alpha+lin(p)*catcher*(1-alpha)
 # Feather the overlapping renders in linear light to avoid denoising/tile seams.
 xs=np.arange(a,aa,dtype='float32')+.5;ys=np.arange(b,bb,dtype='float32')+.5;wx=np.ones_like(xs);wy=np.ones_like(ys)
 if a<x:wx*=np.clip((xs-a)/(x-a),0,1)
 if aa>x2:wx*=np.clip((aa-xs)/(aa-x2),0,1)
 if b<y:wy*=np.clip((ys-b)/(y-b),0,1)
 if bb>y2:wy*=np.clip((bb-ys)/(bb-y2),0,1)
 ww=wy[:,None]*wx[None,:];accum[b:bb,a:aa]+=rgb*ww[:,:,None];weights[b:bb,a:aa]+=ww
for yy in range(0,H,512):
 yy2=min(H,yy+512);orig=lin(photo[yy:yy2].astype('float32')/255)
 value=np.divide(accum[yy:yy2],weights[yy:yy2,:,None],out=orig,where=weights[yy:yy2,:,None]>1e-8)
 out[yy:yy2]=np.clip(np.rint(srgb(value)*255),0,255).astype('uint8')
del accum,weights
if shot=='p13' and (O/'p13_balance_contact_ratio.npy').exists():
 cm=json.loads((O/'p13_balance_contact.json').read_text());a,b,aa,bb=cm['rect'];ratio=np.load(O/'p13_balance_contact_ratio.npy')
 top=np.zeros((H,W),'uint8');poly=np.rint(np.array([[350,1075],[630,1145],[960,1040],[862,994]])*W/1368).astype('int32');cv2.fillPoly(top,[poly],255)
 h=min(bb-b,ratio.shape[0]);w=min(aa-a,ratio.shape[1]);weight=(top[b:b+h,a:a+w].astype('float32')/255)[:,:,None]*(1-fg[b:b+h,a:a+w,3:4].astype('float32')/65535)
 factor=1+(ratio[:h,:w]-1)*weight
 v=srgb(lin(out[b:b+h,a:a+w].astype('float32')/255)*factor);out[b:b+h,a:a+w]=np.clip(np.rint(v*255),0,255).astype('uint8')
cv2.imwrite(str(O/f'{shot}_full_composite.jpg'),out,[cv2.IMWRITE_JPEG_QUALITY,97])
cv2.imwrite(str(O/f'{shot}_full_foreground.png'),fg)
print('FULL_COMPOSITE_COMPLETE',shot,W,H,flush=True)
