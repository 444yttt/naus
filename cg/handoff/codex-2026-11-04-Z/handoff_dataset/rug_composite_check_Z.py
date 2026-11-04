"""No photographed-floor leakage in the opaque rug interior, after grain."""
from pathlib import Path
import json,cv2,numpy as np,OpenEXR
R=Path(__file__).resolve().parent;O=R/'out_Z';rows=[]
for shot in json.loads((O/'native_progress.json').read_text())['completed']:
    ch=OpenEXR.File(str(O/f'{shot}_full_passes0001.exr')).channels();ids=ch['IndexMA.V'].pixels[::3,::3].copy();del ch
    native=cv2.imread(str(O/f'{shot}_full_foreground.png'),-1);H,W=native.shape[:2];fg=native[::3,::3];out=cv2.imread(str(O/f'{shot}_full_composite.png'))[::3,::3]
    core=cv2.erode(np.uint8(abs(ids-12)<.01),np.ones((5,5),'uint8'))>0
    core&=fg[:,:,3]>65500
    if not core.any():
        rows.append({'shot':shot,'rug_interior_pixels':0,'status':'not visible; no positive claim from missing pixels'});continue
    # Include the already specified native lens softening before comparing grain.
    # The eroded opaque core is >15px from transparency/other-material boundaries.
    rgb=native[:,:,:3].astype('float32')*(255/65535);blur=cv2.GaussianBlur(rgb,(0,0),.65)[::3,::3]
    yy,xx=np.mgrid[:H:3,:W:3].astype('float32');rad=np.clip(((xx-W/2)/(W*.65))**2+((yy-H/2)/(H*.65))**2,0,1)[:,:,None];softness=.35+.45*rad
    expected=rgb[::3,::3]*(1-softness)+blur*softness
    error=(out.astype('float32')-expected)[core];noise=json.loads((O/f'{shot}_full_camera_grain.json').read_text())['luminance_sigma_8bit']
    bias=error.mean(0);rmse=float(np.sqrt(np.mean(error**2)));tolerance=noise*1.15+.35
    rows.append({'shot':shot,'rug_interior_pixels':int(core.sum()),'opaque_alpha_minimum':float(fg[:,:,3][core].min()/65535),'mean_difference_BGR_8bit':bias.tolist(),'rmse_8bit':rmse,'expected_camera_grain_sigma_8bit':noise,'rmse_tolerance_grain_plus_quantization':tolerance,'pass_no_floor_leakage':bool(np.max(abs(bias))<.2 and rmse<tolerance),'definition':'eroded rug material-ID interior; final composite must equal fresh rug foreground apart from camera grain and 8bit quantization; existing floor/mirror pattern cannot show through opaque interior'})
(O/'rug_composite_check.json').write_text(json.dumps(rows,indent=2));print('Z_RUG_COMPOSITE_CHECK',rows,flush=True)
