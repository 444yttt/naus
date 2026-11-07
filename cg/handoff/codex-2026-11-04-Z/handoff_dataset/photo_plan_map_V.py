from pathlib import Path
import json,numpy as np,math
from PIL import Image,ImageDraw,ImageFont
R=Path('handoff_dataset');O=R/'out/photo_final_V';C=json.loads((R/'out/layout_V.json').read_text(encoding='utf8'));im=Image.open(R/'images/plan/floorplan_large.jpg').convert('RGB').resize((2000,1365));d=ImageDraw.Draw(im,'RGBA');font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',24);sm=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',19)
def xy(p):return(60+p[0]*88,1182.5-p[1]*88)
def rect(cx,cy,w,h,a):
 a=math.radians(a);co,si=math.cos(a),math.sin(a);return np.array([[cx+co*u-si*v,cy+si*u+co*v] for u,v in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]])
def poly(p,col):d.polygon([xy(v) for v in p],fill=col,outline='#444444',width=2)
for i in C['items']:
 if i['id']=='sofa':
  for m in i['modules']:
   x,y,xx,yy=m['rect'];poly([[x,y],[xx,y],[xx,yy],[x,yy]],'#ece6db')
 else:poly(rect(*i['center'],*i['size'],i['angle']),'#9d9a94' if i['id']=='dining' else '#33383b')
di=next(i for i in C['items'] if i['id']=='dining')
for i in C['chairs']['items']:poly(rect(*i['center'],*i['size'],di['angle']),'#b4b8bc')
for i in C['living_tables']['items']:poly(i['outline_xy'],'#49382f')
for i in C['lounge']['chairs']:poly(rect(*i['center'],*i['size'],i['angle']),'#eae3d6')
t=C['lounge']['table'];x,y=xy(t['center']);rr=t['diameter']*44;d.ellipse((x-rr,y-rr,x+rr,y+rr),fill='#f5f4f0',outline='#444444',width=2)
ip=np.array([[(x-24)/35.2,(473-y)/35.2] for x,y in [(159,230),(194,242),(216,182),(216,120),(201,114)]]);poly(ip,(155,178,181,130));tp=rect(*di['center'],*di['size'],di['angle'])
rows=[]
def near(p,a,b):v=b-a;t=np.clip(np.dot(p-a,v)/np.dot(v,v),0,1);return a+t*v
for a in tp:
 for b,c in zip(ip,np.roll(ip,-1,axis=0)):
  q=near(a,b,c);rows.append((np.linalg.norm(a-q),a,q))
for a in ip:
 for b,c in zip(tp,np.roll(tp,-1,axis=0)):
  q=near(a,b,c);rows.append((np.linalg.norm(a-q),a,q))
gap,a,b=min(rows,key=lambda x:x[0]);d.line([xy(a),xy(b)],fill='#dc4430',width=6)
for p in [a,b]:x,y=xy(p);d.ellipse((x-5,y-5,x+5,y+5),fill='#dc4430')
# Equal-offset stereo triangle and viewing axis.
for sp in [[9.05,.80],[9.05,3.90]]:
 d.line([xy([6.3,2.35]),xy(sp)],fill=(79,111,128,130),width=3)
 x,y=xy(sp);rr=.253*44;d.ellipse((x-rr,y-rr,x+rr,y+rr),fill='#292e31',outline='#10222c',width=2)
d.line([xy([6.3,2.35]),xy([9.345,2.35])],fill=(79,111,128,120),width=3)
d.rectangle((1000,0,1999,1364),fill='white')
lines=['参考例｜原宿3LDK｜予算1,500万円','配置図 V｜試作CG・スピーカー左右対称','Linha Dining 2600×1150／Torii×6','Ernest 幅3600／窓側カウチ','Ernestテーブル 1200×900＋1200×700','Eames Lounge Chair×1／IVRESSE直径600','TV97型クラス／中心高さ1150','Beolab 28：チャコールステイン×ブラックアンスラサイト','新規4写真は構造の参照資料','納品合成は元の撮影写真を使用','赤線：テーブル端〜カウンター端の最短距離 約420mm']
for j,l in enumerate(lines):d.text((1020,14+j*38),l,font=font if j==0 else sm,fill='#29383f')
# TV-wall front elevation. Speaker assemblies share +/-1550mm offsets.
sx=200;ox=1500;floor_y=1010

def elev(y,z):return(ox+(2.35-y)*sx,floor_y-z*sx)
def eb(y0,z0,y1,z1,col):
 aa=elev(y0,z0);bb=elev(y1,z1);d.rectangle((min(aa[0],bb[0]),min(aa[1],bb[1]),max(aa[0],bb[0]),max(aa[1],bb[1])),fill=col,outline='#697176',width=2)
eb(.3,0,4.4,2.35,'#d6d0c7');eb(2.35-2.1473878/2,.546,2.35+2.1473878/2,1.754,'#141a1e')
for yy in [.80,3.90]:
 eb(yy-.06,.40,yy+.06,1.370,'#303438');eb(yy-.035,.15,yy+.035,.43,'#2b3034')
 aa=elev(yy,.025);d.ellipse((aa[0]-.1265*sx,aa[1]-6,aa[0]+.1265*sx,aa[1]+6),fill='#222a30')
 for v in [yy,2.35]:d.line([elev(v,-.12),elev(v,-.30)],fill='#465a65',width=2)
 d.line([elev(yy,-.22),elev(2.35,-.22)],fill='#465a65',width=2)
 q=elev((yy+2.35)/2,-.31);d.text((q[0]-50,q[1]),'1550mm',font=sm,fill='#29383f')
d.text((1030,465),'TV壁面・正面図',font=font,fill='#29383f')
d.text((1030,1100),'画面端〜台座：約350mmずつ／背面離隔も共通',font=sm,fill='#29383f')
d.text((1030,1150),'ソファ中央へ約29°内振り／スピーカー間3100mm',font=sm,fill='#29383f')
d.text((1030,1210),'室寸法・離隔は図面読取による概算。発注用実測図ではない。',font=sm,fill='#5a6267')
im.save(O/'plan_V.png');(O/'clearance_V.json').write_text(json.dumps({'table_island_shortest_edge_clearance_m':float(gap),'closest_points_world':[a.tolist(),b.tolist()],'furniture_moved':'speaker pair only; other approved placements unchanged','status':'approximate raster plan; not survey'},indent=2));print('PLAN_V_SAVED')
