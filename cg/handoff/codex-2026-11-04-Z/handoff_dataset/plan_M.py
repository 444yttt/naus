from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).parent; O=R/'out'
cfg=json.loads((O/'layout_I.json').read_text(encoding='utf-8-sig'))
dining=json.loads((O/'DINING_SELECTION.json').read_text(encoding='utf-8-sig'))
cfg['revision']='M_dining_toward_kitchen';cfg['geometry_note']='Room scale approximate. New table/chairs/Le Club are dimensioned schematic envelopes, not manufacturer CAD contours.'
di=next(i for i in cfg['items'] if i['id']=='dining')
di.update(brand='Minotti',model='Linha Dining',variant='260cm Grigio Orobico',size=[2.6,1.15],height_mm=740,center=[3.816,5.089],outline_status='schematic rectangle at published dimensions',source='https://www.minotti.com/en/linha-dining',product_selection_status='user confirmed',top='Grigio Orobico',base_status='Golden Brown official; black availability unverified')
for key in ['outline_uv','extension_lengths_mm','height_status']:di.pop(key,None)
for it in cfg['items']:
 if it['id'].startswith('speaker'):it.update(finish_reference='Charcoal Stain / Black Anthracite',finish_status='user confirmed',size=[.253,.253])
sofa=next(i for i in cfg['items'] if i['id']=='sofa');sofa['upholstery']='Shedir 02 Burro'
sofa['center'][0]+=.25
for module in sofa['modules']:
 module['rect'][0]+=.25;module['rect'][2]+=.25
for table in cfg['living_tables']['items']:
 table['outline_xy']=[(x+.50,y) for x,y in table['outline_xy']]
cfg['chairs']={'brand':'Minotti','model':'Torii Dining','size_mm':[640,660,870],'base':'fixed','upholstery':'grey fabric, code pending','width_status':'standard64cm assumed for layout; Large not selected','items':[]}
def rect(cx,cy,w,h,a):
 c,s=math.cos(math.radians(a)),math.sin(math.radians(a))
 return [(cx+c*u-s*v,cy+s*u+c*v) for u,v in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
cx,cy=di['center'];a=di['angle'];c,s=math.cos(math.radians(a)),math.sin(math.radians(a))
for side in [-1,1]:
 for u in [-.85,0,.85]:
  v=side*(.575+.33+.02)
  cfg['chairs']['items'].append({'center':[cx+c*u-s*v,cy+s*u+c*v],'size':[.64,.66],'angle':a,'side_sign':side})
cfg['rug']={'brand':'Poliform','model':'Shindo','colour':'Natural','rect':[5.20,.35,8.70,4.35],'size_mm':[4000,3500],'size_status':'provisional layout'}
cfg['lounge']={'chairs':[{'center':[1.70,1.85],'size':[.94,.88],'angle':90,'front_direction':'towards diagonal window'}],'table':{'brand':'Roche Bobois','model':'IVRESSE','center':[1.40,.85],'diameter':.6,'height':.55,'top':'White Carrara'},'geometry_status':'published dimensions; schematic envelope; position proposed'}
cfg['lounge_brief']={'brand':'Poliform','model':'Le Club','quantity_chairs':1,'direction':'diagonal window','upholstery':'Shedir 02 Burro'}
cfg['living_revision']={'sofa_toward_tv_mm':250,'tables_toward_tv_mm':500,'sofa_front_to_table_mm':655,'rug_mm':[4000,3500],'lounge_quantity':1}
cfg['upholstery_coordination']={'items':['Ernest','Le Club single'],'selected':'Shedir 02 Burro'}
island=[((x-24)/35.2,(473-y)/35.2) for x,y in [(159,230),(201,114),(216,120),(194,242)]]
def pointseg(p,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1]; t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def distance(pa,pb):return min([pointseg(p,pb[j],pb[(j+1)%len(pb)]) for p in pa for j in range(len(pb))]+[pointseg(p,pa[j],pa[(j+1)%len(pa)]) for p in pb for j in range(len(pa))])
tablepoly=rect(*di['center'],*di['size'],a)
chairpolys=[rect(*ch['center'],*ch['size'],a) for ch in cfg['chairs']['items']]
window=[(0,0),(4.88,13.1)]
checks={'scale_status':'approximate, not surveyed','table_to_island_m':round(distance(tablepoly,island),2),'chair_to_island_min_m':round(min(distance(p,island) for p in chairpolys),2),'chair_to_diagonal_window_min_m':round(min(min(pointseg(v,*window) for v in p) for p in chairpolys),2),'chair_count':6,'pullout_status':'chairs drawn near table; pullout envelope not guaranteed; check narrow kitchen end','new_geometry':'dimensioned simplified outlines; Ernest table contours preserved from official PDF','rug_size_status':'provisional 4000x3500'}
def overlaps(pa,pb):
 for p in [pa,pb]:
  for i in range(len(p)):
   q,r=p[i],p[(i+1)%len(p)];nx,ny=-(r[1]-q[1]),r[0]-q[0]
   aa=[x*nx+y*ny for x,y in pa];bb=[x*nx+y*ny for x,y in pb]
   if max(aa)<=min(bb)+1e-8 or max(bb)<=min(aa)+1e-8:return False
 return True
furn=[('dining',tablepoly)]+[(f'chair{i}',p) for i,p in enumerate(chairpolys)]
for m in sofa['modules']:
 x0,y0,x1,y1=m['rect'];furn.append(('sofa'+m['id'],rect((x0+x1)/2,(y0+y1)/2,x1-x0,y1-y0,0)))
for i,ch in enumerate(cfg['lounge']['chairs']):furn.append((f'lounge{i}',rect(*ch['center'],*ch['size'],ch['angle'])))
checks['envelope_overlaps']=[(na,nb) for i,(na,pa) in enumerate(furn) for nb,pb in furn[i+1:] if overlaps(pa,pb)]
cfg['checks_J']=checks
im=Image.open(R/'images/plan/floorplan_large.jpg').convert('RGB').resize((2000,1365));d=ImageDraw.Draw(im,'RGBA')
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',22);sm=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',18);title=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',29)
def xy(x,y):return (60+x*88,1182.5-y*88)
def poly(p,col):d.polygon([xy(*v) for v in p],fill=col,outline='#554f48',width=2)
def box(r,col):x0,y0,x1,y1=r;poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],col)
def label(x,y,t):d.text(xy(x,y),t,font=sm,fill='#242c31',stroke_width=2,stroke_fill='#ffffff')
box(cfg['rug']['rect'],(206,193,165,145))
for x in range(round(xy(5.20,0)[0])+8,round(xy(8.70,0)[0]),12):d.line([(x,xy(0,4.35)[1]),(x,xy(0,.35)[1])],fill=(200,187,162,80),width=1)
poly(tablepoly,'#9d9992')
for ch in cfg['chairs']['items']:
 poly(rect(*ch['center'],*ch['size'],a),'#8d9195')
 # Back edge marks the direction of each dining chair.
 p=rect(*ch['center'],*ch['size'],a);edge=(p[0],p[1]) if ch['side_sign']<0 else (p[2],p[3]);d.line([xy(*v) for v in edge],fill='#3d4249',width=5)
for m in sofa['modules']:box(m['rect'],'#3d3029' if m['id']=='F' else '#efe8da')
for t in cfg['living_tables']['items']:poly(t['outline_xy'],'#44322b')
for it in cfg['items']:
 if it['id'] in ['sofa','dining']:continue
 poly(rect(*it['center'],*it['size'],it['angle']),'#252a2c')
for ch in cfg['lounge']['chairs']:
 poly(rect(*ch['center'],*ch['size'],ch['angle']),'#efe8da')
 # Local +Y is the front: arrow makes the window-facing orientation explicit.
 xx,yy=ch['center'];theta=math.radians(ch['angle']);dx,dy=-math.sin(theta),math.cos(theta)
 start=xy(xx,yy);end=xy(xx+dx*.7,yy+dy*.7)
 d.line([start,end],fill='#526b70',width=4)
 for sign in [-1,1]:
  tip=xy(xx+dx*.53+sign*dy*.10,yy+dy*.53-sign*dx*.10)
  d.line([end,tip],fill='#526b70',width=4)
t=cfg['lounge']['table'];px,py=xy(*t['center']);rad=t['diameter']*44;d.ellipse((px-rad,py-rad,px+rad,py+rad),fill='#f4f1ed',outline='#444444',width=2)
d.line([xy(9.40,.3),xy(9.40,4.4)],fill='#b5a48c',width=7)
d.ellipse((496,298,526,328),fill='#343b36');label(5.1,10.05,'Balance')
label(3.9,5.05,'1');label(5.95,2.2,'2');label(7.5,2.4,'3');label(5.2,.25,'4');label(1.9,1.5,'5');label(1.6,.85,'6');label(9.0,2.55,'7')
d.rectangle((1010,0,1999,420),fill='white')
lines=['配置案 M｜最新選定を反映','1 Linha Dining：2600×1150／Torii固定脚×6','   Grigio Orobico／チェアはグレー布・品番未定','2 Ernest：幅3600／窓側カウチ奥行1700','3 Ernest：1200×900＋1200×700 パズル配置','4 Shindo Natural：4000×3500 仮サイズ','5 Le Club×1：940×880／ソファと同じShedir02','6 IVRESSE：直径600×H550／白カララ','7 LG83型＋Beolab28：Charcoal Stain×Black Anthracite','室内寸法は概算／新規家具の外形は寸法ベースの略図','L案からダイニング一式をカウンター方向へ200mm移動','カウンターとの離隔は概算／椅子を引く余裕は要調整']
for j,l in enumerate(lines):d.text((1025,12+j*35),l,font=title if j==0 else sm,fill='#28343b')
im.save(O/'plan_M.png');im.save(O/'plan_latest.png')
im.crop((20,490,1000,1210)).resize((1470,1080)).save(O/'plan_M_detail.png')
(O/'layout_M.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8');(O/'layout_draft.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8')
(O/'plan_M_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(checks,ensure_ascii=False))





