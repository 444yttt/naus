from pathlib import Path
import json,zipfile,shutil
from PIL import Image,ImageDraw,ImageFont
import numpy as np
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_U';G=R/'out/photo_geometry_U';D=O/'review';D.mkdir(exist_ok=True);names=['n01','n02','n03','n04'];labels={'n01':'写真1｜リビング・窓の角','n02':'写真2｜バルコニー正面','n03':'写真3｜TV壁側','n04':'写真4｜ダイニング・キッチン'};font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',25);sm=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',20)
qa=[];board=Image.new('RGB',(1640,2260),'#f5f2ed');dd=ImageDraw.Draw(board);comparison=[]
for k,n in enumerate(names):
 p=O/f'{n}_preview_composite.jpg';im=Image.open(p).convert('RGB');src=Image.open(R/f'images/photos/{n}.jpg').convert('RGB');assert im.size==src.size==(960,1280)
 alpha=Image.open(O/f'{n}_preview_alpha.png');assert np.array(alpha).max()>0;settings=json.loads((O/f'{n}_preview_render_settings.json').read_text(encoding='utf8'));assert settings['camera']['revision']=='U';ref=json.loads((O/f'{n}_floor_reflection_settings.json').read_text());assert 'unit-emission' in ref['method']
 qa.append({'shot':n,'native_size':[960,1280],'composite_size':list(im.size),'all_frame':True,'rug':False,'camera':settings['camera']['C'],'sun':settings['lighting']['sun'],'status':'source-resolution composition; architectural calibration approximate'})
 x=k%2*820;y=k//2*1130;dd.text((x+15,y+10),labels[n],font=font,fill='#2b3940');board.paste(im.resize((795,1060)),(x+12,y+55));shutil.copy2(p,D/f'{n}_U_native.jpg')
 row=Image.new('RGB',(1640,1130),'#f5f2ed');dr=ImageDraw.Draw(row);dr.text((15,10),labels[n]+'｜元写真',font=font,fill='#2b3940');dr.text((835,10),'U｜ラグなし・床反射',font=font,fill='#2b3940');row.paste(src.resize((795,1060)),(12,55));row.paste(im.resize((795,1060)),(832,55));comparison.append(row)
board.save(O/'U_new_four_views.jpg',quality=95)
allim=Image.new('RGB',(1640,4520),'white')
for j,im in enumerate(comparison):allim.paste(im,(0,1130*j))
allim.save(O/'U_new_before_after.jpg',quality=93)
# Show the old erroneous T fit next to the counter-anchored U repair.
a=Image.open(R/'out/photo_composite_T/u2_preview_composite.jpg');b=Image.open(O/'u2_preview_composite.jpg');pair=Image.new('RGB',(1640,700),'#f5f2ed');dr=ImageDraw.Draw(pair);dr.text((15,10),'旧T｜カメラの対応に誤り',font=font,fill='#2b3940');dr.text((835,10),'U｜キッチン角を含めて再推定',font=font,fill='#2b3940');a.thumbnail((795,610));b.thumbnail((795,610));pair.paste(a,(12,60));pair.paste(b,(832,60));pair.save(O/'U_dining_gap_correction.jpg',quality=95)
(O/'U_delivery_QA.json').write_text(json.dumps(qa,indent=2),encoding='utf8')
readme='''# U｜新規撮影4枚へ反映

新しい写真4枚へ、同じ家具配置を合成。各960×1280の原寸。切り抜き・引き伸ばしなし。ラグは一旦撤去。

前のTでは、窓だけの対応を重視し、u2/p01のカメラ推定を誤った。図面上で約42cmの天板間隔が、合成では大きく離れて見えていた。Uは実写のキッチンの天板角・脚元と窓を一緒に使って解き直した。図面上の家具配置は維持。配置変更で隙間を隠す処理はしていない。

写真1=n01：窓の角。写真2=n02：バルコニー正面。写真3=n03：TV壁とバルコニー。写真4=n04：ダイニングとキッチン。

新しい日差しの低さに合わせ、影と家具への光を再計算。床反射は、追加家具の反射光と物理的な反射マスクを別レンダー。反射光はマスクで割り戻したHDR光量を露出換算・トーンマップしてから再合成し、元写真の床の白飛びを避けている。元写真の窓の映り込みは背景として保持。古いHall_returnの閉じた壁の仮形状が、新写真のTV壁やダイニングを切り欠いていたため、写真上の遮蔽には使わない。

4枚は元写真の画素数で出力した確認用合成。カメラ校正・材質・測光が実測で確定した最終画像という意味ではない。図面の寸法はラスター画像からの概算。新規写真に有効な焦点距離EXIFはなく、写真1は室内範囲の制約付きの暫定解。写真2/3も建具位置の図面読み取りに残差がある。写真4のキッチン角の対応を重視している。

U_dining_gap_correction.jpgは旧Tと修正Uの比較。photo_plan_U.pngは写真の推定位置と約42cmの寸法箇所。U_new_before_after.jpgは全4枚の元写真と合成。
''';(D/'README.md').write_text(readme,encoding='utf8');(O/'README.md').write_text(readme,encoding='utf8')
for p in [O/'U_new_four_views.jpg',O/'U_new_before_after.jpg',O/'U_dining_gap_correction.jpg',G/'photo_plan_U.png',G/'NEW_PHOTO_REGISTER.md',G/'clearance_U.json',O/'U_delivery_QA.json']:
 shutil.copy2(p,D/p.name)
with zipfile.ZipFile(O/'U_new_photos.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for p in D.iterdir():z.write(p,p.name)
print('U_REVIEW_READY',json.dumps(qa),flush=True)
