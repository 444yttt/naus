"""Assemble only completed native originals, with verifiable delivery metadata."""
from pathlib import Path
import json, hashlib, zipfile, shutil,subprocess,sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageCms, ImageOps

R=Path(__file__).resolve().parent
O=R/'out/photo_final_V'
D=O/'delivery'
D.mkdir(exist_ok=True)
shots=['u1','u2','p09','p01','p13']
labels=['リビング・テレビ壁','リビングからダイニング','窓際からリビング','ダイニング','キッチン']
# Compute a separate before/after environment ray test: covering a bright window
# direction is different from covering an equally sized dark interior direction.
for shot in shots:
    occ=O/f'{shot}_full_floor_reflection_environment_occluded_passes0001.exr'
    if not occ.exists():
        with (O/f'{shot}_directional_occlusion.log').open('w',encoding='utf8') as log:
            subprocess.run([str(R/'runtime/blender-4.5.9-windows-x64/blender.exe'),'-b','--python',str(R/'photo_floor_reflection_V.py'),'--',shot,'--occlusion-only'],stdout=log,stderr=subprocess.STDOUT,check=True)
        assert occ.exists(),('Directional reflection pass missing',shot)
    subprocess.run([sys.executable,str(R/'photo_composite_V.py'),shot,'full'],check=True)
subprocess.run([sys.executable,str(R/'photo_verify_V.py')],check=True)
icc=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',26)
small=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',19)
report=[]; thumbs=[]; pairs=[]
for i,(shot,label) in enumerate(zip(shots,labels),1):
    src=R/f'images/photos/{shot}.jpg'
    png=O/f'{shot}_full_composite.png'
    if not png.exists():
        raise RuntimeError(f'Native output not complete: {shot}')
    im=Image.open(png).convert('RGB'); orig=Image.open(R/f'images/photos_srgb/{shot}.png').convert('RGB')
    assert im.size==orig.size,(shot,im.size,orig.size)
    effect=Image.open(O/f'{shot}_effect_mask.png').convert('L')
    # Independent check: untouched architectural pixels remain the source photo.
    # Sparse sampling keeps QA memory small even for 24 MP originals.
    a=np.asarray(orig)[::5,::5].astype('int16');b=np.asarray(im)[::5,::5].astype('int16')
    keep=np.asarray(effect)[::5,::5]==0
    untouched_error=float(np.abs(a-b)[keep].max()) if keep.any() else None
    assert untouched_error is None or untouched_error<=2,(shot,'background changed outside effect',untouched_error)
    settings=json.loads((O/f'{shot}_render_settings.json').read_text(encoding='utf8'))
    assert settings['render_percentage']==100
    refl=json.loads((O/f'{shot}_full_floor_reflection_settings.json').read_text())
    fit=json.loads((O/f'{shot}_full_reflection_fit.json').read_text())
    grain=json.loads((O/f'{shot}_full_camera_grain.json').read_text())
    assert refl['resolution_percentage']==50
    name=f'{i:02d}_{shot}'
    im.save(D/f'{name}.jpg',quality=98,subsampling=0,icc_profile=icc)
    im.save(D/f'{name}.png',compress_level=6,icc_profile=icc)
    report.append({'shot':shot,'title':label,'native_size':list(im.size),'original_size':list(orig.size),'foreground_resolution_percent':100,'reflection_resolution_percent':50,'untouched_source_max_error_8bit':untouched_error,'reflection_fit':fit,'camera_grain':grain,'jpeg_sha256':hashlib.sha256((D/f'{name}.jpg').read_bytes()).hexdigest()})
    cw=860; ch=round(im.height*cw/im.width)
    tile=Image.new('RGB',(920,ch+95),'#f5f3ef');dr=ImageDraw.Draw(tile)
    dr.text((30,18),f'{i:02d}  {label}',font=font,fill='#292929')
    tile.paste(im.resize((cw,ch),Image.Resampling.LANCZOS),(30,70));thumbs.append(tile)
    pw=760;ph=round(im.height*pw/im.width)
    pair=Image.new('RGB',(1600,ph+90),'#f5f3ef');dr=ImageDraw.Draw(pair)
    dr.text((30,16),f'{i:02d}  {label} ／ 撮影写真 → 合成',font=font,fill='#292929')
    pair.paste(orig.resize((pw,ph),Image.Resampling.LANCZOS),(30,65))
    pair.paste(im.resize((pw,ph),Image.Resampling.LANCZOS),(810,65));pairs.append(pair)

cols=2; rows=(len(thumbs)+1)//2
heights=[max(t.height for t in thumbs[j*2:j*2+2]) for j in range(rows)]
sheet=Image.new('RGB',(1840,sum(heights)+110),'#f5f3ef');dr=ImageDraw.Draw(sheet)
dr.text((30,20),'参考例・原宿3LDK ／ 試作CG 最終版',font=font,fill='#292929')
dr.text((30,65),'元の撮影写真5視点・ラグなし・共通配置',font=small,fill='#666666')
y=110
for j,h in enumerate(heights):
    for k in range(2):
        idx=j*2+k
        if idx<len(thumbs):sheet.paste(thumbs[idx],(k*920,y))
    y+=h
subprocess.run([sys.executable,str(R/'photo_overview_V.py')],check=True)
comparison=Image.new('RGB',(1600,sum(p.height for p in pairs)),'#f5f3ef');y=0
for pair in pairs:comparison.paste(pair,(0,y));y+=pair.height
comparison.save(D/'06_before_after.jpg',quality=94,icc_profile=icc)
shutil.copy2(O/'plan_V.png',D/'07_plan.png')
shutil.copy2(O/'speaker_layout_V.json',D/'speaker_layout.json')
shutil.copy2(R/'out/layout_V.json',D/'layout.json')
shutil.copytree(O/'verification',D/'verification',dirs_exist_ok=True)
manifest=json.loads((R/'out/3d_R/model_manifest.json').read_text(encoding='utf8'))
manifest=[m for m in manifest if m['item']!='Shindo']
for m in manifest:
    if m['item']=='Beolab28 pair':m['note']+='; Charcoal Stain / Black Anthracite visual recreation; symmetric Y0.80 / 3.90 at X9.05m'
    if m['item']=='Ernest sofa':m['note']+='; pale Shedir 02 Burro visual reference; actual fabric appearance not colorimetrically measured'
(D/'model_sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
if (O/'scene_delivery_QA.json').exists():shutil.copy2(O/'scene_delivery_QA.json',D/'scene_delivery_QA.json')
shutil.copy2(O/'colour_management.json',D/'colour_management.json')
(D/'delivery_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
readme='''参考例・原宿3LDK ／ 試作CG 最終版

ピッチ動画・スライド・ホームページ用の参考例です。納品実績・確定した施工／発注プランではありません。

01〜05：元の撮影写真を背景にした5視点。JPGとPNGは同内容、原寸・sRGB。
00：一覧、06：撮影写真との全画面比較、07：共通配置図。
verification/：各視点の床線・鉛直・モデル底面と再投影残差。誤差値は合わせ込みの残差を含み、独立した実測精度ではありません。
layout.json：全視点で共通の家具配置（m）。モデルの入手先と再構成の範囲はmodel_sources.jsonに記載。
追加撮影4枚は構造確認だけに使用し、納品合成の背景には使用していません。
Display P3の撮影写真はICCプロファイルを解釈してsRGBへ変換。元画像は別に保管しています。

配置
・TV97型クラス、中心高さ1150mm。Beolab 28はTV中心から左右1550mmずつ。
  画面端〜スピーカー台座は左右とも概算350mm、背面位置も共通。
  両機をソファ中央へ約29度内振り。音響実測に基づく調整ではありません。
・Ernestソファ、パズル状のErnestテーブル2台、Linha Dining、Torii Dining6脚、
  Eames Lounge Chair1脚、IVRESSE、Beosound Balance。リビングのラグは外しています。

合成処理
家具の接地影と間接光、床に映る家具、既存の窓・外景反射の遮蔽を処理。
環境反射は家具を置く前後の光線を比較。写真との整合が取れる視点では、遮る方向の明るさまで反映しています。
床の拡散成分と反射成分を分離し、影だけで既存反射を一律に暗くしない構成。
CGの表面には撮影写真から推定した微細な明度ノイズを合わせています。
背景と家具本体は原寸。ぼける床反射と空室の影補正参照は縦横50%で計算して原寸に再サンプリング。
視点ごとの家具移動、背景の生成置換、部分レンダーの使い回しは行っていません。

精度について
間取りの縮尺、カメラ、光源、床の反射率は図面と写真からの推定です。
HDR環境光・レンズ実測・材料の実測値はないため、物理的完全一致を保証する資料ではありません。
公式配布モデルを優先し、一部は第三者データまたは寸法に合わせた再構成を使用。
Beolab 28・Balance・Eamesは公式データ、Ernestは販売店配布データ、Linha・Toriiは第三者データ。
TV外形・IVRESSE・ソファ背面テーブル・タイル仕上げは寸法／参考写真から再構成しています。
発注・施工・購入前は実測および販売店確認が必要です。予算1500万円は参考例の設定です。
'''
(D/'README.txt').write_text(readme,encoding='utf-8-sig')
with zipfile.ZipFile(O/'Harajuku_3LDK_delivery_V.zip','w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for f in sorted(D.rglob('*')):
        if f.is_file():z.write(f,f.relative_to(D))
print(json.dumps({'delivery':str(D),'views':len(report),'zip':str(O/'Harajuku_3LDK_delivery_V.zip')},ensure_ascii=False))
