"""Diagnostic source-by-source contribution sheet, with one consistent display scale."""
from pathlib import Path
import json,sys
import numpy as np,OpenEXR
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_S'
path=Path(sys.argv[1]) if len(sys.argv)>1 else next((O/'p09_tiles').glob('p09_1024_2048_passes*.exr'))
f=OpenEXR.File(str(path));channels=f.channels();panels=[];stats={}
labels=[('Image','CG合計'),('Combined_Direct_sun','直射光'),('Combined_Balcony_sky','バルコニー窓の天空光'),('Combined_Diagonal_sky','斜め窓の天空光'),('Combined_Ambient_sky','環境光'),('Combined_Downlight_01','ダウンライト 1'),('Combined_Exterior_reflection','外景の映り込み'),('DiffInd','間接の拡散反射')]
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',25)
for key,label in labels:
 if key not in channels:continue
 a=channels[key].pixels[:,:,:3].astype('float32');a=np.maximum(np.nan_to_num(a),0)
 stats[key]={'mean_linear_RGB':a.mean((0,1)).tolist(),'p99_linear_luminance':float(np.percentile(a@np.array([.2126,.7152,.0722]),99))}
 # The same diagnostic exposure/Reinhard function for all sources; not final AgX.
 v=a*(2**-1.5);v=v/(1+v);v=np.where(v<=.0031308,v*12.92,1.055*v**(1/2.4)-.055)
 im=Image.fromarray(np.clip(v*255,0,255).astype('uint8')).resize((540,540),Image.Resampling.LANCZOS)
 panel=Image.new('RGB',(580,620),'#efeeea');panel.paste(im,(20,60));dr=ImageDraw.Draw(panel);dr.text((20,15),label,font=font,fill='#222222');panels.append(panel)
sheet=Image.new('RGB',(580*4,620*2),'#efeeea')
for i,p in enumerate(panels):sheet.paste(p,((i%4)*580,(i//4)*620))
sheet.save(O/'light_source_breakdown.jpg',quality=95)
(O/'light_source_breakdown.json').write_text(json.dumps({'source_exr':str(path),'display':'equal diagnostic exposure, Reinhard; not final composite display','tile_only_statistics':stats},ensure_ascii=False,indent=2),encoding='utf8')
print('LIGHT_SOURCE_BREAKDOWN_SAVED')
