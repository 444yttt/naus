"""Cross-view foreground check before expensive native sweep; never final PASS."""
from pathlib import Path
import cv2,numpy as np,OpenEXR,json,sys
R=Path(__file__).resolve().parent;O=R/'out_Z';rows=[]
def lin(v):return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
def cct(c):
    xyz=np.array([[.4124564,.3575761,.1804375],[.2126729,.7151522,.0721750],[.0193339,.1191920,.9503041]])@c;x,y=xyz[:2]/xyz.sum();n=(x-.332)/(y-.1858);return float(-449*n**3+3525*n*n-6823.3*n+5520.33)
variant=sys.argv[1] if len(sys.argv)>1 else 'base'
for shot,png in [('u1',O/'u1_preview_foreground.png'),('p09',O/'light_trials/p09_material_sheen45.png')]:
    if variant=='warm350':png=O/f'light_trials/{shot}_sheen45_warm350.png'
    if variant=='sky800':png=O/f'light_trials/{shot}_sheen45_sky800.png'
    ch=OpenEXR.File(str(O/f'{shot}_preview_passes0001.exr')).channels();norm=np.stack([ch['Normal.'+a].pixels for a in 'XYZ'],2);ids=ch['IndexMA.V'].pixels.copy();del ch
    raw=cv2.imread(str(png),-1);rgb=lin(raw[:,:,:3][:,:,::-1].astype('float32')/65535);base=(cv2.erode(np.uint8(abs(ids-8)<.01),np.ones((3,3),'uint8'))>0)&(raw[:,:,3]>65000);faces=[]
    for axis in range(3):
        for sign in [-1,1]:
            m=base&(norm[:,:,axis]*sign>.9)
            if m.sum()<60:continue
            c=rgb[m].mean(0);faces.append({'axis':axis,'sign':sign,'pixels':int(m.sum()),'RGB':c.tolist(),'Y':float(c@np.array([.2126,.7152,.0722])),'CCT_proxy_K':cct(c),'green_excess':float(c[1]-(c[0]+c[2])/2)})
    vals=raw[:,:,:3][base];rows.append({'shot':shot,'faces':faces,'face_std_Y':float(np.std([f['Y'] for f in faces])),'sofa_channel_clipping_fraction':float((vals>=65534).mean()),'scope':'quarter-resolution foreground only; final native composite metrics required'})
f=[v for r in rows for v in r['faces']];a=[v['CCT_proxy_K'] for v in f if v['axis']==1 and v['sign']==-1];b=[v['CCT_proxy_K'] for v in f if v['axis']==1 and v['sign']==1];result={'views':rows,'window_minus_Y_CCT_proxy':float(np.mean(a)) if a else None,'room_plus_Y_CCT_proxy':float(np.mean(b)) if b else None,'window_warmer_in_preview':bool(a and b and np.mean(a)<np.mean(b)),'caveat':'original normal-based colour diagnostic retained, includes internal cushion faces; not measured illuminant temperature'}
(O/f'candidate_material_QA_{variant}.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
