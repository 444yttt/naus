from pathlib import Path
import json,shutil,zipfile
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_T';G=R/'out/photo_geometry_T';D=O/'review';D.mkdir(exist_ok=True)
names=['u1','u2','p01','p09','p13'];labels={'u1':'TV側','u2':'ダイニング全景','p01':'ダイニング正面','p09':'リビング・窓の角','p13':'キッチン側'}
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',25);sm=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',19)
rows=[];qa=[]
for n in names:
 src=Image.open(R/f'images/photos/{n}.jpg').convert('RGB');dst=Image.open(O/f'{n}_preview_composite.jpg').convert('RGB');W,H=src.size
 assert dst.size==(int(W*.2),int(H*.2)),(n,src.size,dst.size)
 settings=json.loads((O/f'{n}_preview_render_settings.json').read_text(encoding='utf8'));assert settings['camera']['revision']=='T' if n!='u1' else True
 assert (O/f'{n}_floor_reflection_settings.json').exists()
 alpha=np.array(Image.open(O/f'{n}_preview_alpha.png'));count=int((alpha>0).sum());assert count>20
 qa.append(dict(shot=n,source_size=list(src.size),review_size=list(dst.size),full_frame=True,scale_percent=20,foreground_pixels=count,render_complete='PHOTO_RENDER_COMPLETE' in (O/f'{n}_preview.log').read_text(encoding='utf8',errors='replace'),reflection_complete=(O/f'{n}_floor_reflection_furniture_passes0001.exr').exists() and (O/f'{n}_floor_reflection_opacity_passes0001.exr').exists()))
 hh=round(src.height*700/src.width);board=Image.new('RGB',(1440,hh+72),'#f4f2ee');dr=ImageDraw.Draw(board);dr.text((15,8),f'{n}｜{labels[n]}   元写真',font=font,fill='#263641');dr.text((735,8),'T｜ラグなし・共通配置・床反射',font=font,fill='#263641');board.paste(src.resize((700,hh)),(10,60));board.paste(dst.resize((700,hh)),(730,60));rows.append(board)
 shutil.copy2(O/f'{n}_preview_composite.jpg',D/f'{n}_T_review.jpg')
large=Image.new('RGB',(1440,sum(x.height for x in rows)),'white');yy=0
for im in rows:large.paste(im,(0,yy));yy+=im.height
large.save(O/'T_before_after_full_frame.jpg',quality=93)
thumb=Image.new('RGB',(1800,1700),'#f4f2ee');dr=ImageDraw.Draw(thumb)
for i,n in enumerate(names):
 im=Image.open(O/f'{n}_preview_composite.jpg');im.thumbnail((570,770));x=(i%3)*600;y=(i//3)*850;thumb.paste(im,(x+(600-im.width)//2,y+55));dr.text((x+15,y+12),f'{n}｜{labels[n]}',font=font,fill='#263641')
dr.text((1215,910),'T｜配置修正・全画面プレビュー',font=font,fill='#263641');dr.text((1215,980),'ラグなし／床の反射を別計算',font=sm,fill='#263641');dr.text((1215,1030),'原寸の最終レンダーではありません',font=sm,fill='#263641');thumb.save(O/'T_five_views.jpg',quality=95)
(O/'image_full_frame_QA.json').write_text(json.dumps(qa,indent=2),encoding='utf8')
for p in [G/'photo_plan_correspondence_T.png',G/'PHOTO_RANGE_REGISTER.md',G/'independent_architecture_direction_checks.json',O/'image_full_frame_QA.json',O/'scene_full_frame_QA.json',O/'T_before_after_full_frame.jpg',O/'T_five_views.jpg']:
 assert p.exists(),p;shutil.copy2(p,D/p.name)
text='''# T｜写真と図面の対応を修正した確認版

元写真を全画面で使った5視点の20%解像度プレビューです。原寸の最終合成ではありません。

- 斜めFIX窓を、鋭角の端D0から短い一枚も含めて番号付け。u2はD2〜、p01はD3〜へ対応を修正。
- キッチン天板を、元図面の五角形へ修正。以前の四角形では右側の折れ点を省いていました。
- 家具は各写真で同じ配置・寸法を使用。画面へ収めるために家具を写真別に移動・変形していません。
- ラグは暫定撤去。建築と外景は元の写真を維持。
- 影は拡散反射の床受け面で計算。床への家具の映り込みは、追加家具の反射光と、同じ床BRDFを通した白色モデルの反射マスクを別計算して合成。既存建築の仮モデルの反射は混ぜず、写真にある窓の反射への遮蔽も含みます。
- 5枚とも全画面レンダー。Sの部分境界やタイルは流用していません。画面端で家具が切れる場合は、共通配置から投影した実際の見切れです。

写真と図面の対応はphoto_plan_correspondence_T.png、全19枚の範囲の整理はPHOTO_RANGE_REGISTER.mdに記録。個室の写真をLDKに混ぜていません。参照写真のすべてをカメラ校正済みとはしていません。

図面には室内の寸法線がないため、室寸法はラスター図からの概算です。窓の合わせ込みの点と、別に検査した線を区別しています。窓合わせの小さな残差は実測精度を保証しません。天板の一部にも図面の粗さ・観測点の曖昧さに由来する残差があります。

光の強さ、床の粗さ、外景の明るさは写真からの推定です。HDR環境や実測の照度はありません。床反射の光量はCGと同じ露出換算を使った初期値で、完全な測光一致ではありません。Sを完成版として使わず、この対応修正を以後の基準にします。
'''
(D/'README.md').write_text(text,encoding='utf8');(O/'README.md').write_text(text,encoding='utf8')
with zipfile.ZipFile(O/'T_review.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for p in D.iterdir():z.write(p,p.name)
print('T_REVIEW_READY',json.dumps(qa))
