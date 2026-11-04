from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).parent;O=R/'out'
cfg=json.loads((O/'layout_N.json').read_text(encoding='utf8'))
di=next(i for i in cfg['items'] if i['id']=='dining')
sofa=next(i for i in cfg['items'] if i['id']=='sofa')
def rect(cx,cy,w,h,a):
 c,s=math.cos(math.radians(a)),math.sin(math.radians(a))
 return [(cx+c*u-s*v,cy+s*u+c*v) for u,v in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
cx,cy=di['center'];a=di['angle'];c,s=math.cos(math.radians(a)),math.sin(math.radians(a))
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
lines=['配置案 N｜最新選定を反映','1 Linha Dining：2600×1150／Torii固定脚×6','   Grigio Orobico／チェアはグレー布・品番未定','2 Ernest：幅3600／窓側カウチ奥行1700','3 Ernest：1200×900＋1200×700 パズル配置','4 Shindo Natural：4000×3500 仮サイズ','5 Owen×1：1060×880／ソファと同じShedir02','6 IVRESSE：直径600×H550／白カララ','7 LG83型＋Beolab28：Charcoal Stain×Black Anthracite','室内寸法は概算／新規家具の外形は寸法ベースの略図','M案の家具配置を維持／ラウンジのみOwenへ変更','カウンターとの離隔は概算／椅子を引く余裕は要調整']
for j,l in enumerate(lines):d.text((1025,12+j*35),l,font=title if j==0 else sm,fill='#28343b')
im.save(O/'plan_N.png');im.save(O/'plan_latest.png')
im.crop((20,490,1000,1210)).resize((1470,1080)).save(O/'plan_N_detail.png')
(O/'layout_N.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8');(O/'layout_draft.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8')
(O/'plan_N_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(checks,ensure_ascii=False))





