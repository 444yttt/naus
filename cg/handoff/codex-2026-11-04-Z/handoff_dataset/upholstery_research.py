from pathlib import Path
from html.parser import HTMLParser
import json,sys
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).parent;F=R/'reference';O=R/'out'
class P(HTMLParser):
 def __init__(self):super().__init__();self.items={}
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and 'data-product-layer-category' in a:
   key=(a.get('data-product-layer-category'),a.get('data-product-layer-title'))
   self.items[key]={'category':key[0],'colour':key[1],'image':a.get('data-product-layer-image'),'url':a.get('data-product-layer-url')}
ps=[]
for n in ['ernest','leclub']:
 p=P();p.feed((F/f'{n}_materials.html').read_text(encoding='utf8'));ps.append(p)
selected=[('Shedir','02 Burro'),('Shire','04 Sabbia'),('Nabuk','01 Latte')]
items=[]
for key in selected:
 assert key in ps[0].items and key in ps[1].items,key
 item=ps[1].items[key];item['available_on']=['Ernest','Le Club'];items.append(item)
 path=F/f'swatch_{key[0]}_{key[1].split()[0]}.jpg'
 item['local_image']=str(path)
manifest=[{'url':i['image'],'path':i['local_image']} for i in items]+[{'url':'https://s3.poliform.it/2025/07/poliform-essenza-olmo-nero.jpg','path':str(F/'swatch_black_elm.jpg')}]
(O/'swatch_downloads.json').write_text(json.dumps(manifest),encoding='utf8')
if '--manifest' in sys.argv:
 print(json.dumps(manifest));sys.exit()
result={'status':'researched candidates; not approved','sources':['https://www.poliform.it/en/products/ernest-sofa/','https://www.poliform.it/en/products/le-club-armchairs/'],'matching_codes':items,'recommendation':'Shedir02 Burro','dark_wood_table':'user indicates dark wood table; treat all-dark-wood as current working finish; exact finish final confirmation pending','notes':['Both product HTML lists contain the same fabric/leather codes','Online colours are not physical samples','Ernest removable cover, Le Club non-removable cover']}
(O/'upholstery_candidates.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
im=Image.new('RGB',(1500,900),'#f4f1e9');d=ImageDraw.Draw(im)
title=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',30);font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',24);small=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',19)
d.text((30,20),'Ernest × Le Club：共通で選べる明るい張地',font=title,fill='#263437')
labels=[('Shedir 02 Burro','第一候補：暖かみのある明るい布','コットン100％'),('Shire 04 Sabbia','サンド系・織りの表情を楽しむ','ビスコース・ポリエステル・綿など'),('Nabuk 01 Latte','淡色のヌバックレザー','起毛した革のしっとりした表情')]
for i,(item,lab) in enumerate(zip(items,labels)):
 x=25+i*495;d.rounded_rectangle((x,90,x+475,750),radius=16,fill='white')
 pic=ImageOps.fit(Image.open(item['local_image']).convert('RGB'),(435,330));im.paste(pic,(x+20,115))
 wood=ImageOps.fit(Image.open(F/'swatch_black_elm.jpg').convert('RGB'),(435,105));im.paste(wood,(x+20,455))
 for j,line in enumerate(lab):d.text((x+20,585+j*42),line,font=font if j==0 else small,fill='#263437')
d.text((30,790),'上：Poliform公式の張地画像／下：ブラックエルムの公式画像。実物の色・縮尺とは異なります。',font=small,fill='#52605d')
d.text((30,830),'ErnestとLe Clubの両製品の掲載リストで、同じ素材・色番を確認。最終選定は現物サンプルで。',font=small,fill='#52605d')
im.save(O/'upholstery_comparison.png')
print(json.dumps(items,ensure_ascii=False,indent=2))
