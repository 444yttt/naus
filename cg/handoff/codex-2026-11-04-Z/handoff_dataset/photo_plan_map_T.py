from pathlib import Path
import json,math,numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;O=R/'out/photo_geometry_T';C=json.loads((R/'out/layout_Q.json').read_text(encoding='utf8'));fit=json.loads((O/'architecture_fit.json').read_text(encoding='utf8'));C['revision']='T_no_rug_architecture_recheck';C['rug']['enabled']=False;C['rug']['status']='omitted provisionally per user request';C['architecture_status']='raster plan approximate; rechecked window pane IDs and five-vertex island';(R/'out/layout_T.json').write_text(json.dumps(C,ensure_ascii=False,indent=2),encoding='utf8')
# Draw registered plan using the SAME raster->metre transform as architecture fit.
im=Image.open(R/'images/plan/floorplan_large.jpg').convert('RGB').resize((2000,1365));d=ImageDraw.Draw(im,'RGBA');font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',23);small=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',19)
def xy(p):x,y=p;return(60+x*88,1182.5-y*88)
def poly(pp,col):d.polygon([xy(p) for p in pp],fill=col,outline='#444444',width=2)
def rect(cx,cy,w,h,a):
 a=math.radians(a);c,s=math.cos(a),math.sin(a);return [[cx+c*u-s*v,cy+s*u+c*v] for u,v in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
for v in C['items']:
 if v['id']=='sofa':
  for m in v['modules']:
   x,y,xx,yy=m['rect'];poly([[x,y],[xx,y],[xx,yy],[x,yy]],'#eee7d8')
 else:poly(rect(*v['center'],*v['size'],v['angle']),'#a6a19a' if v['id']=='dining' else '#32363a')
for v in C['chairs']['items']:poly(rect(*v['center'],*v['size'],C['chairs'].get('angle',next(i for i in C['items'] if i['id']=='dining')['angle'])),'#c6c9cc')
for t in C['living_tables']['items']:poly(t['outline_xy'],'#49372d')
for v in C['lounge']['chairs']:poly(rect(*v['center'],*v['size'],v['angle']),'#eae3d5')
tt=C['lounge']['table'];xx,yy=xy(tt['center']);rr=tt['diameter']*44;d.ellipse((xx-rr,yy-rr,xx+rr,yy+rr),fill='#eeeeea',outline='#444444',width=2)
d.line([xy([9.4,.3]),xy([9.4,4.4])],fill='#aa9982',width=7)
for k,(x,y) in enumerate(fit['window_nodes_plan_pixels']):
 px,py=x*2.5,y*2.5;d.ellipse((px-7,py-7,px+7,py+7),fill='#d52c3c');d.text((px-55,py-25),f'D{k}',fill='#d52c3c',font=font,stroke_width=2,stroke_fill='white')
colors={'u1':'#dd7515','u2':'#1471ba','p01':'#7059b4','p03':'#3f8d52','p09':'#cb335b','p13':'#098d92'}
for n in ['u1','u2','p01','p03','p09','p13']:
 c=json.loads((O/f'{n}_camera.json').read_text(encoding='utf8')) if (O/f'{n}_camera.json').exists() else json.loads((R/f'out/photo_composite_S/{n}_camera.json').read_text(encoding='utf8'));rot=np.array(c['R']);pos=np.array(c['C']);center=xy(pos[:2]);col=colors[n]
 dirs=[]
 for u in [0,c['W']]:
  ray=rot.T@[(u-c['W']/2)/c['f'],0,1];ray=ray[:2]/np.linalg.norm(ray[:2]);end=pos[:2]+ray*2.7;dirs.append(end);d.line([center,xy(end)],fill=col,width=4)
 ray=rot.T@[0,0,1];ray=ray[:2]/np.linalg.norm(ray[:2]);d.line([center,xy(pos[:2]+ray*1.9)],fill=col,width=5)
 x,y=center;d.ellipse((x-8,y-8,x+8,y+8),fill=col);offset={'p09':(10,-48),'u2':(10,5),'p01':(5,-35),'p13':(-70,-35),'p03':(-80,5),'u1':(-45,12)}[n];d.text((x+offset[0],y+offset[1]),n,fill=col,font=font,stroke_width=2,stroke_fill='white')
d.rectangle((1000,0,1999,630),fill='white')
lines=['写真と図面の対応確認 T／ラグなし','赤いD0〜D6：斜めFIX窓の支柱・端部','D0から短い一枚を含めて順に数え直し','矢印：撮影位置と左右の視線（推定）','u1：TV壁・リビング・バルコニー側','u2：ダイニング・斜めFIX・キッチン手前','p01：ダイニングと斜めFIX中央部','p03：角の短いFIX窓・ラウンジ付近','p09：バルコニー＋角のFIX・リビング','p13：キッチン・斜めFIX奥側','アイランドは図面の五角形を採用','室寸法はラスター図面からの概算','線の一致は実測精度を保証しない','周辺の参照写真は写真台帳で区別']
for j,l in enumerate(lines):d.text((1020,15+j*41),l,font=font if j==0 else small,fill='#25343e')
im.save(O/'photo_plan_correspondence_T.png');im.save(R/'out/plan_T.png')
# Full source inventory; don't invent precise camera positions for reference-only views.
rows={'u1':('LDK・TV側','テレビ壁／窓頭／バルコニー建具','Tで元の壁コーナー基準を保持'), 'u2':('LDK・ダイニング側','D2〜D5の窓頭、D2〜D4の窓下端','Tで再計算'), 'p01':('LDK・ダイニング側','D3・D4の窓頭と窓下端','Tで再計算'), 'p02':('LDK・ダイニング側','p01と重なるFIX窓、キッチン手前端','参照用・カメラ未計算'), 'p03':('LDK・鋭角コーナー側','D0〜D2の窓頭と窓下端','Tで再計算'), 'p04':('バルコニー側','引違い建具、両脇の袖壁','参照用・カメラ未計算'), 'p05':('LDK・バルコニー側','引違い建具、天井梁、床への窓反射','参照用・カメラ未計算'), 'p06':('LDK・鋭角コーナー側','短いFIX、斜めFIX窓頭、天井折れ線','参照用・カメラ未計算'), 'p07':('キッチン・窓側','シンク、斜めFIX、窓際の天井折れ線','参照用・カメラ未計算'), 'p08':('キッチン奥側','アイランド、奥の窓、下がり天井','参照用・カメラ未計算'), 'p09':('LDK・TV側から角を見る','D0〜D2、バルコニー建具、梁、空調開口','Tで再計算'), 'p10':('LDK・バルコニー側','引違い建具、窓頭、床の反射','参照用・カメラ未計算'), 'p11':('LDK・バルコニー側','引違い建具、梁、床の反射','参照用・カメラ未計算'), 'p12':('LDK・バルコニーと角側','バルコニー建具、角柱、FIX窓、天井','参照用・カメラ未計算'), 'p13':('キッチン奥を見る','D4〜D6窓頭、露出した窓下端、五角形天板','Tで再計算'), 'p14':('キッチンからLDK側','シンク、バルコニー建具、天井','参照用・カメラ未計算'), 'p15':('個室','窓と柱、壁、天井','LDK合成対象外・個室番号は未特定'), 'p16':('個室','p15と同じ窓・柱','LDK合成対象外・個室番号は未特定'), 'p17':('個室','窓・壁・天井','LDK合成対象外・個室番号は未特定')}
lines=['# 写真と図面の対応台帳 T','','撮影範囲とカメラ座標の推定を分けて記録。元図面に寸法線がないため、絶対寸法は概算。','窓番号は鋭角コーナーD0から。最初の短い一枚も数える。','','|写真|写る領域|建築基準|状態|','|---|---|---|---|']
for n,(a,b,c) in rows.items():lines.append(f'|{n}|{a}|{b}|{c}|')
lines.extend(['','## 修正根拠','','- Sでu2の最初の見える支柱をD1相当としていたが、角の短い一枚と写真p03の支柱をたどるとD2に対応する。p01の中央もD3へ修正。','- キッチンの天板は図面上で五角形。Sは右側の折れ点を省いた四角形とし、奥端と折れ点を取り違えた。Tは五角形へ戻した。','- 自動の床特徴点照合は一致が乏しく、反射を拾う組もあったため位置の確定根拠に採用していない。','- 窓の上下端は合わせ込みに使った点。独立した検証点ではない。天井線やカウンターの残差は別途確認する。','- ラグは一旦撤去。家具形状・配置の共通モデルは維持。画像ごとの見栄えで家具を動かさない。','- 全画面プレビューを先に検査。Sの部分レンダー境界・タイルキャッシュは再利用しない。'])
(O/'PHOTO_RANGE_REGISTER.md').write_text('\n'.join(lines),encoding='utf8')
print('PLAN_AND_REGISTER_SAVED')

