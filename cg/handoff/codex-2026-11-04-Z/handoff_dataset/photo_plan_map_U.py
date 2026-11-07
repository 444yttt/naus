from pathlib import Path
import json,numpy as np,math
from PIL import Image,ImageDraw,ImageFont
R=Path('handoff_dataset');O=R/'out/photo_geometry_U';C=json.loads((R/'out/layout_T.json').read_text(encoding='utf8'));im=Image.open(R/'images/plan/floorplan_large.jpg').convert('RGB').resize((2000,1365));d=ImageDraw.Draw(im,'RGBA');font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',24);sm=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',19)
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
colors=['#0d88a1','#6b579b','#d48124','#3b9967']
for k,col in zip(range(1,5),colors):
 n=f'n{k:02}';c=json.loads((O/f'{n}_camera.json').read_text());pos=np.array(c['C']);rot=np.array(c['R']);st=xy(pos[:2]);fwd=rot.T@[0,0,1];fwd=fwd[:2]/np.linalg.norm(fwd[:2]);d.line([st,xy(pos[:2]+fwd*2)],fill=col,width=5);x,y=st;d.ellipse((x-7,y-7,x+7,y+7),fill=col);d.text((x+12,y-25),f'写真{k}',fill=col,font=font,stroke_width=2,stroke_fill='white')
d.rectangle((1000,0,1999,635),fill='white');lines=['配置・新規写真の対応 U','家具の配置は共通／ラグなし','赤線：天板同士の最短距離 約42cm','（ラスター図面からの概算）','前の版で離れて見えたのはカメラのずれ','キッチンの角と窓割りを併用して再推定','写真1：バルコニーと斜めFIXの角','写真2：バルコニー正面','写真3：TVの壁とバルコニー','写真4：ダイニングとキッチン','カメラの印は推定位置・視線','元写真の解像度：各960×1280','新規4枚は全画面・原寸で合成','実測の図面・測光校正ではない']
for j,l in enumerate(lines):d.text((1020,14+j*42),l,font=font if j==0 else sm,fill='#29383f')
im.save(O/'photo_plan_U.png');(O/'clearance_U.json').write_text(json.dumps({'table_island_shortest_edge_clearance_m':float(gap),'closest_points_world':[a.tolist(),b.tolist()],'furniture_moved':False,'status':'approximate raster plan; not survey'},indent=2));print('PLAN_U_SAVED')
