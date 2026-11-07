from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json
R=Path(__file__).parent;F=R/'reference';O=R/'out'
out=Image.new('RGB',(1500,780),'#f5f2eb');d=ImageDraw.Draw(out)
title=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',30);font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',22)
d.text((30,20),'窓辺のラウンジ：ラグジュアリー × スタイリッシュ',font=title,fill='#29373b')
data=[('Poliform Le Club','leclub','低くワイドな彫刻的フォルム','Ernestと揃う、ゆったりした佇まい'),('B&B Italia Husk','husk','立体的なクッションが主役','ヘッドレスト付き・回転式も候補'),('Minotti Torii Bold','torii','繊細な縫製＋ブロンズの脚元','今回のラグジュアリー方向の本命')]
for i,(name,key,a,b) in enumerate(data):
 x=20+495*i;d.rounded_rectangle((x,90,x+475,680),radius=15,fill='white')
 pic=Image.open(F/f'luxury_{key}.jpg').convert('RGB')
 # Product images contain broad studio margins; retain each complete composition.
 pic=ImageOps.contain(pic,(445,420));out.paste(pic,(x+(475-pic.width)//2,110+(420-pic.height)//2))
 d.text((x+20,550),name,font=font,fill='#29373b')
 d.text((x+20,600),a,font=font,fill='#59615e');d.text((x+20,635),b,font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',18),fill='#59615e')
d.text((30,715),'メーカー公式写真／縮尺不同。候補比較であり、仕上げ・購入・配置の確定ではありません。',font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',19),fill='#59615e')
out.save(O/'lounge_luxury_shortlist.png')
(O/'lounge_luxury_brief.json').write_text(json.dumps({'status':'unselected shortlist','priority':'luxury and stylish; comfortable time as couple; recline/high back not mandatory','quantity':2,'candidates':[{'brand':'Poliform','model':'Le Club','source':'https://www.poliform.it/en/products/le-club-armchairs/'},{'brand':'B&B Italia','model':'Husk armchair','source':'https://www.bebitalia.com/en-us/en-us-husk-poltrone.html'},{'brand':'Minotti','model':'Torii Bold armchair','source':'https://www.minotti.com/en/torii-bold_armchair'}],'domestic_prices':'not verified; do not use earlier recliner prices'},ensure_ascii=False,indent=2),encoding='utf8')
