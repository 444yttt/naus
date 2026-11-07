from pathlib import Path
import cv2,numpy as np,json
R=Path(__file__).resolve().parent;O=R/'out_X';W=R/'out/photo_final_W'
def lum(p):
 im=cv2.imread(str(p))[::2,::2].astype('float32')/255;im=np.where(im<=.04045,im/12.92,((im+.055)/1.055)**2.4);return im@np.array([.0722,.7152,.2126],dtype='float32')
a=lum(W/'u2_full_composite.png');b=lum(O/'u2_full_composite.png');p=lum(R/'images/photos_srgb/u2.png');cw=cv2.imread(str(W/'u2_full_reflection_coverage.png'),0)[::2,::2]/255;cx=cv2.imread(str(O/'u2_full_reflection_coverage.png'),0)[::2,::2]/255;alpha=cv2.imread(str(O/'u2_full_alpha.png'),0)[::2,::2];h,w=a.shape;roi=np.zeros_like(a,dtype=bool);roi[int(h*.60):int(h*.82),int(w*.09):int(w*.30)]=True
for t in [.22,.5,.8,.95]:
 m=roi&(cw>t)&(cx>t)&(alpha<2);print(t,int(m.sum()),[(k,float(v[m].mean())) for k,v in [('W',a),('X',b),('photo',p),('Wcoverage',cw),('Xcoverage',cx)]],flush=True)
