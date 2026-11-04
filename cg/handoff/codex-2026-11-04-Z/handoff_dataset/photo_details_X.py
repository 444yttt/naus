from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageCms
import json
R=Path(__file__).resolve().parent;O=R/'out_X';D=O/'delivery/details';D.mkdir(parents=True,exist_ok=True)
import subprocess,sys
subprocess.run([sys.executable,str(R/'photo_contacts_check_X.py')],check=True)
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',24)
# Native-pixel crops: 1 source pixel = 1 output pixel, no enlargement invented.
boxes={'u2':[(100,2200,1700,3500),(2750,2450,5100,3550)],'p01':[(1100,2550,2800,3900)],'u1':[(0,3250,3000,4850),(2800,4000,4284,5712)],'p09':[(500,2350,2600,3800)],'p13':[(0,2650,1450,3850)]}
boxes['u2'].append((4600,2150,5712,3200));boxes['p13'].append((600,2200,1800,3100))
icc=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
for shot,rects in boxes.items():
 old=Image.open(R/f'out/photo_final_W/{shot}_full_composite.png');new=Image.open(O/f'{shot}_full_composite.png')
 for i,box in enumerate(rects):
  box=(box[0],box[1],min(box[2],new.width),min(box[3],new.height));a=old.crop(box);b=new.crop(box)
  sheet=Image.new('RGB',(a.width*2,a.height+60),'#f5f3ef');dr=ImageDraw.Draw(sheet);dr.text((15,12),f'{shot} 原寸 ／ W',font=font,fill='#222');dr.text((a.width+15,12),'X／レビュー用',font=font,fill='#222');sheet.paste(a,(0,60));sheet.paste(b,(a.width,60));sheet.save(D/f'{shot}_{i+1:02d}_native_comparison.jpg',quality=97,subsampling=0,icc_profile=icc)
if (O/'scene_inspection.json').exists():
 import shutil;shutil.copy2(O/'scene_inspection.json',D/'scene_inspection.json')
print('W_NATIVE_DETAILS_READY')
