from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json
R=Path(__file__).parent;O=R/'out';F=R/'reference'
rows=[
 {'model':'BoConcept Tilburg','size_mm':[760,850,1080],'price_jpy_from':292900,'pair_jpy_from':585800,'price_scope':'chair only, listed starting price without adjustable headrest; selected headrest/upholstery costs need quote','features':'swivel, pushback recline, optional adjustable headrest','url':'https://www.boconcept.com/ja-jp/p/tilburg/4061540-3:24-9:0075-14:3256/','selection':'recommended shortlist, not user approved'},
 {'model':'Stressless Tokyo Highback Star','size_mm':[800,810,1100],'price_jpy_range':[398200,460900],'pair_jpy_range':[796400,921800],'price_scope':'2026-04 Japanese official leather price list illustrated with footstool; confirm package scope in dealer quote','features':'recline, rocking, footstool; adjustable-headrest lowback variant same price band','url':'https://www.stressless.com/ja-jp/-/media/stresslesssite/aboutus/service/pricelistsjapan/recliner_price_leather_260401.pdf','selection':'shortlist, not user approved'},
 {'model':'Vitra Grand Relax','size_mm':[690,810,1060],'price_jpy_from':960300,'pair_jpy_from':1920600,'price_scope':'official shop starting configuration; ottoman and upgrades additional unless confirmed promotion applies','features':'360 swivel, synchronized recline, adjustable resistance and position lock','url':'https://store.vitra.co.jp/products/grand-relax','selection':'shortlist, not user approved'}]
(O/'lounge_shortlist.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
im=Image.new('RGB',(1500,950),'#f6f4ef');d=ImageDraw.Draw(im)
title=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',30);font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',22);small=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',18)
d.text((35,22),'夫婦でゆったり過ごす窓辺：ラウンジチェア候補',font=title,fill='#23333b')
stress=Image.open(F/'stressless_page6.png').crop((324,524,447,674))
imgs=[Image.open(F/'lounge_tilburg.png'),stress,Image.open(F/'lounge_grandrelax_full.jpg')]
names=['BoConcept Tilburg','Stressless Tokyo','Vitra Grand Relax']
lines=[['幅76×奥行85cm','回転＋リクライニング','調整式ヘッドレストも選択可','2脚 58.6万円〜 ※本体の最安仕様'],['幅80×奥行81cm','ハイバック＋リクライニング','ロッキング／オットマンで足を支える','掲載価格：1組39.8〜46.1万円'],['幅69×奥行81cm','回転＋シンクロリクライニング','好みの角度で固定可能','2脚 192.1万円〜 ※オットマン別']]
for i,(pic,name,desc) in enumerate(zip(imgs,names,lines)):
 x=25+i*495;d.rounded_rectangle((x,95,x+475,830),radius=18,fill='white')
 if pic.mode=='RGBA':
  bg=Image.new('RGBA',pic.size,'white');bg.alpha_composite(pic);pic=bg.convert('RGB')
 pic=ImageOps.contain(pic.convert('RGB'),(430,430));im.paste(pic,(x+(475-pic.width)//2,135+(430-pic.height)//2))
 d.text((x+20,585),name,font=font,fill='#23333b')
 for j,line in enumerate(desc):d.text((x+20,635+j*37),line,font=small,fill='#44545a')
d.text((35,865),'掲載価格は税込・仕様で変動。寸法は通常時。倒した時の設置範囲は選定後に確認。',font=small,fill='#44545a')
d.text((35,900),'写真はメーカー資料。色の指定ではありません。座り心地はご夫婦それぞれの試座で確認。',font=small,fill='#44545a')
im.save(O/'lounge_shortlist.png')
