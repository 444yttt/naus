"""Full-frame contact sheet with one landscape hero and four portrait views."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageCms
R=Path(__file__).resolve().parent;D=R/'out/photo_final_V/delivery'
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',28);sm=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',23)
hero=Image.open(D/'02_u2.png').convert('RGB');hw=1760;hh=round(hero.height*hw/hero.width)
portraits=[('01_u1','01  リビング・テレビ壁'),('03_p09','03  窓際からリビング'),('04_p01','04  ダイニング'),('05_p13','05  キッチン')]
cw=860;rows=[]
for j in range(2):
    tiles=[]
    for filename,label in portraits[j*2:j*2+2]:
        im=Image.open(D/f'{filename}.png').convert('RGB');h=round(im.height*cw/im.width)
        tile=Image.new('RGB',(cw,h+55),'#f5f3ef');dr=ImageDraw.Draw(tile);dr.text((0,6),label,font=sm,fill='#292929');tile.paste(im.resize((cw,h),Image.Resampling.LANCZOS),(0,55));tiles.append(tile)
    row=Image.new('RGB',(1760,max(t.height for t in tiles)),'#f5f3ef')
    for k,t in enumerate(tiles):row.paste(t,(k*900,0))
    rows.append(row)
sheet=Image.new('RGB',(1840,110+55+hh+40+sum(r.height+35 for r in rows)+10),'#f5f3ef');dr=ImageDraw.Draw(sheet)
dr.text((40,18),'参考例・原宿3LDK・予算1,500万円 ／ 試作CG 最終版',font=font,fill='#292929')
dr.text((40,65),'元の撮影写真5視点・ラグなし・全視点共通配置',font=sm,fill='#666666')
dr.text((40,116),'02  リビングからダイニング',font=sm,fill='#292929')
sheet.paste(hero.resize((hw,hh),Image.Resampling.LANCZOS),(40,165));y=165+hh+40
for row in rows:sheet.paste(row,(40,y));y+=row.height+35
icc=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes();sheet.save(D/'00_overview.jpg',quality=95,icc_profile=icc)
print('OVERVIEW_SAVED',sheet.size)
