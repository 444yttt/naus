from pathlib import Path
import json, math
import pdfplumber
from PIL import Image,ImageDraw,ImageFont
from calligaris_geometry import objgroups,hull
import numpy as np
R=Path(__file__).parent; O=R/'out'
cfg=json.loads((O/'layout_draft.json').read_text(encoding='utf8'))
pdf=R/'reference/Ernest_official.pdf'
page=pdfplumber.open(pdf).pages[63]
def outline(index,w,h):
 c=page.curves[index]; pts=[]; last=None
 for cmd in c['path']:
  if cmd[0] in ('m','l'):last=cmd[1];pts.append(last)
  elif cmd[0]=='c':
   p0=last;p1,p2,p3=cmd[1:]
   for j in range(1,17):
    t=j/16;q=1-t;pts.append(tuple(q**3*p0[k]+3*q*q*t*p1[k]+3*q*t*t*p2[k]+t**3*p3[k] for k in (0,1)))
   last=p3
 return [((x-c['x0'])/c['width']*w,(y-c['top'])/c['height']*h) for x,y in pts]
a=outline(4,1.2,.9);b=outline(12,1.2,.7)
# Match the supplied red-table photograph: opposing cutouts with a half-length
# stagger. The old aligned bounding boxes incorrectly made a solid rectangle.
# 600mm longitudinal stagger, 400mm transverse offset; nominal20mm mating gap.
tables=[{'name':'1200×900','size_mm':[1200,900],'outline_uv':a}, {'name':'1200×700','size_mm':[1200,700],'outline_uv':[(.6-u,1.10-v) for u,v in b]}]
for t in tables:t['outline_xy']=[(6.73+v,2.20+u) for u,v in t['outline_uv']]
modules=[
 {'id':'A','name':'窓側・端部座面','size_mm':[900,1010],'rect':[5.315,.55,6.325,1.45]},
 {'id':'B','name':'中央座面','size_mm':[900,1010],'rect':[5.315,1.45,6.325,2.35]},
 {'id':'C','name':'中央座面','size_mm':[900,1010],'rect':[5.315,2.35,6.325,3.25]},
 {'id':'D','name':'キッチン側プーフ','size_mm':[900,690],'rect':[5.675,3.25,6.365,4.15]},
 {'id':'E','name':'窓側・足置きプーフ','size_mm':[900,690],'rect':[6.325,.55,7.015,1.45]},
 {'id':'F','name':'背面テーブル','size_mm':[850,360],'rect':[5.315,3.275,5.675,4.125]}]
cfg['revision']='I_calligaris_dining'
cfg['project_presentation']={'title':'参考例｜原宿3LDK｜予算1,500万円','budget_jpy':15000000,'status':'試作CG・提案例。納品実績や確定見積ではない','location_label_source':'user supplied; not independently verified'}
cfg['lounge_brief']={'area':'lower-left window corner of plan','quantity_chairs':2,'arrangement':'small round coffee table with chairs angled inward, preserve window circulation','selection_status':'not selected; recommendations only','candidates':[{'brand':'Poliform','model':'Le Club','size_mm':[940,880,670],'source':'https://www.poliform.it/us/products/le-club-armchairs/'},{'brand':'Poliform','model':'Loai','size_mm':[655,620,715],'source':'https://www.poliform.it/us/products/loai/'}]}
cfg['lounge_brief'].update({'brand':'Poliform','model':'Le Club','selection_status':'User chose Poliform after Le Club comparison; proceed with Le Club pair as working selection','size_mm':[940,880,670],'quantity_chairs':2,'finish_status':'colour and fabric/leather not selected','side_table_status':'small round table desired; product and size not selected','layout_status':'not yet placed in current drawing; verify official footprint and window circulation before next layout'})
cfg['lounge_brief']['finish_status']='Match Ernest sofa upholstery: same material, colour and fabric/leather code where offered on both models; exact code not yet selected and joint availability must be verified'
cfg['upholstery_coordination']={'items':['Poliform Ernest sofa','Poliform Le Club pair'],'intent':'same upholstery material and colour, preferably identical manufacturer code','selection_status':'user confirmed coordination; specific upholstery not selected','verification_required':'shared upholstery availability on both products'}
cfg['upholstery_coordination'].update({'light_colour_direction':'user requested light upholstery against dark wood tables','verified_shared_candidates':['Shedir02 Burro','Shire04 Sabbia','Nabuk01 Latte'],'recommendation':'Shedir02 Burro; not user approved','source_evidence':'reference/ernest_materials.html and reference/leclub_materials.html; exact material+colour keys matched','excluded_candidate':'Shire02 Avorio not listed for Le Club in retrieved current page'})
sofa=next(x for x in cfg['items'] if x['id']=='sofa')
sofa.update({'center':[5.82,2.35],'size':[3.6,1.01],'modules':modules,'total_width_mm':3600,'chaise_depth_mm':1700,'kitchen_end_depth_mm':1050,'size_status':'dimensions from official catalogue pp120-121; assembly proposal, dealer approval not obtained','recess_span_estimate_m':4.1,'nominal_width_margin_m':.25})
cfg['living_tables'].update({'items':tables,'geometry_status':'official p124 vector outlines; 700 rotated180 then staggered -600mm longitudinal/+400mm transverse; nominal20mm mating gap; outer envelope1800x1100mm','placement_status':'reference-photo stagger, proposed room position; room scale approximate','arrangement':'opposing cutouts with600mm stagger as supplied photo, not a filled rectangular group','geometry_reference':'https://s3.poliform.it/2025/05/poliform-coffeetable-ernest-lifestyle-09.jpg'})
di=next(x for x in cfg['items'] if x['id']=='dining')
di.update({'brand':'Calligaris','model':'ICARO','variant':'CS4114-R 160 rectangular, fully extended','size':[2.4,.9],'extension_lengths_mm':[1600,2000,2400],'height_status':'current Japan page770mm; supplied2018 CAD ceramic760mm; resolve current finish/version before final CG','source':'https://calligaris-japan.com/4891104','product_selection_status':'user specified; finish not selected','outline_status':'top projection from official OBJ, normalized to official2400x900mm envelope'})
cg=objgroups(R/'reference/Oleandro_CS2031/cs2031.obj')
cv=np.concatenate(list(cg.values()));cmin=cv.min(axis=0);cmax=cv.max(axis=0)
def chairpts(v):return [((x-(cmin[0]+cmax[0])/2)/(cmax[0]-cmin[0])*.58,(z-(cmin[2]+cmax[2])/2)/(cmax[2]-cmin[2])*.575) for x,y,z in v]
chairparts={k:hull(chairpts(v)) for k,v in cg.items() if k in ('schienale','seduta')}
cfg['chairs'].update({'brand':'Calligaris','model':'OLEANDRO','size_mm':[580,575],'product_selection_status':'user specified series; wood/metal legs and upholstery not selected; common plan envelope','footprint_status':'official CS2031 OBJ seat/back projections normalized to official580x575mm; woodCS2034 shares published plan dimensions','sources':['https://calligaris-japan.com/4890590','https://calligaris-japan.com/4903281'],'parts_uv':chairparts})
cx,cy=di['center'];th=math.radians(di['angle']);c,s=math.cos(th),math.sin(th)
cfg['chairs']['items']=[]
for side in (-1,1):
 for u in (-.78,0,.78):
  v=side*.7525
  cfg['chairs']['items'].append({'center':[cx+c*u-s*v,cy+s*u+c*v],'size':[.58,.575],'angle':di['angle'],'side_sign':side,'side':'window' if side==1 else 'room','front_direction':'toward table','placement_gap_to_top_mm':15})
tg=objgroups(R/'reference/Icaro_CS4114/cs4114-r_160.obj')
tv=np.concatenate([v for k,v in tg.items() if '__open' in k and ('piano_top_160' in k or 'piano_top_aperto_160' in k)])
tmin=tv.min(axis=0);tmax=tv.max(axis=0)
di['outline_uv']=hull([((x-(tmin[0]+tmax[0])/2)/(tmax[0]-tmin[0])*2.4,(z-(tmin[2]+tmax[2])/2)/(tmax[2]-tmin[2])*.9) for x,y,z in tv])
cfg['sources']=[{'url':'https://s3.poliform.it/2025/04/Poliform_catalog_ERNEST_2024.pdf','sofa_pages':'120-121','coffee_table_pages':'124-125'}]
cfg['sources'] += [{'url':'https://calligaris-japan.com/4891104','product':'ICARO CS4114-R160','cad_download':'https://calligaris-japan.com/__/download/6978382988ddea0637227c80/cs4114-r-160.zip'},{'url':'https://calligaris-japan.com/4890590','product':'OLEANDRO CS2031','cad_download':'https://calligaris-japan.com/__/download/6978257fcdcc65032d3b999d/cs2031.zip'},{'url':'https://calligaris-japan.com/4903281','product':'OLEANDRO CS2034','cad_download':'https://calligaris-japan.com/__/download/697c5b226ffe18302d3f8b30/cs2034.zip'}]
(O/'layout_I.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8')
(O/'layout_draft.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8')
im=Image.open(R/'images/plan/floorplan_large.jpg').convert('RGB').resize((2000,1365));d=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',24);small=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',20)
def xy(x,y):return (60+x*88,1182.5-y*88)
def poly(pts,fill,outline='#344c5c',width=2):d.polygon([xy(*p) for p in pts],fill=fill,outline=outline,width=width)
def box(rect,fill):
 x0,y0,x1,y1=rect;poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],fill)
for it in cfg['items']:
 if it['id']=='sofa':continue
 x,y=it['center'];a0,b0=it['size'];th=math.radians(it['angle']);c,s=math.cos(th),math.sin(th)
 coords=it['outline_uv'] if it['id']=='dining' else [(-a0/2,-b0/2),(a0/2,-b0/2),(a0/2,b0/2),(-a0/2,b0/2)]
 poly([(x+c*u-s*v,y+s*u+c*v) for u,v in coords],'#c5a476' if it['id']=='dining' else '#424950')
 if it['id']=='dining':
  for u in (-.8,.8):d.line([xy(x+c*u-s*(-.45),y+s*u+c*(-.45)),xy(x+c*u-s*.45,y+s*u+c*.45)],fill='#8f7552',width=2)
for chair in cfg['chairs']['items']:
 x,y=chair['center'];th=math.radians(70.7);c,s=math.cos(th),math.sin(th)
 for key,col in [('seduta','#dfd3bf'),('schienale','#ad9b80')]:
  pts=[]
  for u,forward in chairparts[key]:
   v=-chair['side_sign']*forward;pts.append((x+c*u-s*v,y+s*u+c*v))
  poly(pts,col,width=1)
for m in modules:
 box(m['rect'],'#57514b' if m['id']=='F' else '#d2dfe2')
 x0,y0,x1,y1=m['rect'];px,py=xy((x0+x1)/2,(y0+y1)/2);d.text((px-8,py-14),m['id'],font=small,fill='white' if m['id']=='F' else '#20323a')
 if m['id'] in 'ABC':
  d.line([xy(x0+.30,y0+.04),xy(x0+.30,y1-.04)],fill='#7e929b',width=3)
for i,t in enumerate(tables):poly(t['outline_xy'],'#847a6c' if i==0 else '#b3a89b')
d.line([xy(9.40,.3),xy(9.40,4.4)],fill='#a9937a',width=6)
px,py=xy(5.0,.55);qx,qy=xy(5.0,4.15);d.line((px,py,qx,qy),fill='#305b76',width=2)
for y in (.55,4.15):d.line([xy(4.92,y),xy(5.08,y)],fill='#305b76',width=2)
d.text((px-105,(py+qy)/2-12),'3600',font=font,fill='#305b76')
d.ellipse((496,298,526,328),fill='#526c54');d.text((532,296),'Balance',font=small,fill='#263b29')
d.rectangle((1015,8,1990,365),fill='white')
lines=['配置案 I：指定製品の公式寸法・データを反映','ダイニング：Calligaris ICARO CS4114-R 160','最大拡張2400×900mm／拡張板400mm×2','椅子：OLEANDRO 580×575mm ×6（3脚＋3脚）','天板・椅子は公式OBJ投影輪郭を使用','椅子は天板から15mm離す仮配置／引く動線は別確認','Ernestソファ全幅3600／窓側カウチ奥行1700mm','中央：1200×900＋1200×700をずらして接合','部屋寸法は概算／家具の仕上げ・椅子脚仕様は未確定','ICARO高さは現行ページと同梱旧CADに差：要照合']
for j,line in enumerate(lines):d.text((1030,14+j*34),line,font=small,fill='#263847')
# Clear dimensioned furniture detail on a separate panel with no room raster.
im.save(O/'plan_I.png')
im.save(O/'plan_latest.png')
im.crop((160,420,970,1200)).save(O/'plan_I_detail.png')
im.crop((160,520,720,1040)).resize((1120,1040)).save(O/'dining_I_detail.png')
# Enlarged footprint drawing paired with the exact reference photo.
sheet=Image.new('RGB',(1500,980),'#fafafa');sd=ImageDraw.Draw(sheet)
title=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',30)
sd.text((35,20),'Ernest 1200×900 ＋ 1200×700：ずらして噛み合わせ',font=title,fill='#243440')
sd.text((35,70),'製品輪郭：公式寸法図から抽出／配置：参考写真に合わせた案',font=font,fill='#44545d')
scale=350
for i,t in enumerate(tables):
 pts=[(80+(u+.6)*scale,160+v*scale) for u,v in t['outline_uv']]
 sd.polygon(pts,fill='#6e665b' if i==0 else '#aaa093',outline='#2b3338',width=3)
sd.text((80,590),'組み合わせ外形：約1800×1100mm',font=font,fill='#243440')
sd.text((80,630),'長手600mmのずらし／接合すき間 約20mmの案',font=small,fill='#44545d')
from PIL import ImageOps
ref=Image.open(R/'reference/life-09.jpg').crop((100,550,825,805))
ref=ImageOps.contain(ref,(690,500));sheet.paste(ref,(780,200))
sd.text((800,560),'ユーザー指定と同じ公式写真',font=font,fill='#243440')
sd.text((35,880),'ダイニング：ICARO 2400×900mm／椅子：OLEANDRO 580×575mm ×6。',font=font,fill='#44545d')
sheet.save(O/'ernest_pair_I.png')
# Independent raster check: the two sampled official top outlines must not overlap.
import numpy as np
masks=[]
for t in tables:
 mask=Image.new('1',(1900,1200));md=ImageDraw.Draw(mask)
 md.polygon([(round((u+.65)*1000),round((v+.05)*1000)) for u,v in t['outline_uv']],fill=1)
 masks.append(np.asarray(mask))
overlap=int(np.logical_and(*masks).sum())
if overlap:raise ValueError(f'Table top overlap: {overlap} square-mm raster cells')
(O/'plan_I_checks.json').write_text(json.dumps({'table_overlap_mm2_raster':overlap,'raster_pitch_mm':1,'coffee_pair_envelope_mm':[1800,1100],'dining_product_status':'ICARO selected;2400x900mm','chair_count':len(cfg['chairs']['items']),'chair_dimensions_mm':[580,575]},indent=2))
print('saved I; official dining projections and6 chairs; coffee table overlap=0')
