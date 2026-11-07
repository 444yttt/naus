"""Publish the inspected W revision without overwriting V or its OneDrive link."""
from pathlib import Path
from PIL import Image,ImageCms,ImageDraw,ImageFont,ImageOps
import numpy as np,json,shutil,zipfile,hashlib
R=Path(__file__).resolve().parent;V=R/'out/photo_final_W';O=R/'out_X';D=O/'delivery';D.mkdir(exist_ok=True)
icc=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
shots=['u1','u2','p09','p01','p13'];labels=['リビング・テレビ壁','リビングからダイニング','窓際からリビング','ダイニング','キッチン']
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',27);small=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',19)
report=[];thumbs=[];pairs=[]
import subprocess,sys
# Use the final common composite settings for every finished camera, including
# views completed before the last numerical occlusion correction.
for shot in shots:subprocess.run([sys.executable,str(R/'photo_composite_X.py'),shot,'full'],check=True)
subprocess.run([sys.executable,str(R/'photo_details_X.py')],check=True)
for i,(shot,label) in enumerate(zip(shots,labels),1):
 im=Image.open(O/f'{shot}_full_composite.png').convert('RGB');source=Image.open(R/f'images/photos_srgb/{shot}.png').convert('RGB')
 assert im.size==source.size,(shot,im.size,source.size)
 a=np.asarray(im)[::7,::7].astype('int16');b=np.asarray(source)[::7,::7].astype('int16');mask=np.asarray(Image.open(O/f'{shot}_effect_mask.png'))[::7,::7]
 err=int(np.abs(a-b)[mask==0].max()) if (mask==0).any() else 0
 assert err<=2,(shot,'untouched plate changed',err)
 stem=f'{i:02d}_{shot}';im.save(D/f'{stem}.jpg',quality=98,subsampling=0,icc_profile=icc);im.save(D/f'{stem}.png',icc_profile=icc)
 settings={'revision':'X','baseline_W':json.loads((V/f'{shot}_refinement.json').read_text()),'changes':['table+6chairs rigid assembly','Eames broad return light and wood response','sofa local seam AO and micro-specular','u2/p13 bounded pinhole refit','p01 floor specular tint'],'geometry':'W repaired Eames surface unchanged','samples':24,'foreground_resolution_percent':100,'reflection_resolution_percent':50}
 for item in settings.get('mesh',[]):
  if item['object'].startswith('SEAT-FABRIC'):
   for key in list(item):
    if key not in ['object','original_vertices']:item.pop(key)
   item.update(surface_version=2,source_components=5,repair='interpolated visible pad envelopes; timber-covered rear skin omitted; fine relief simplified')
 report.append({'shot':shot,'native_dimensions':list(im.size),'unchanged_plate_max_error_8bit':err,'camera':('refitted from W' if shot in ['u2','p13'] else 'unchanged from W'),'render':settings,'grain':json.loads((O/f'{shot}_full_camera_grain.json').read_text()),'sha256':hashlib.sha256((D/f'{stem}.jpg').read_bytes()).hexdigest()})
 width=860;h=round(im.height*width/im.width);tile=Image.new('RGB',(920,h+90),'#f5f3ef');dr=ImageDraw.Draw(tile);dr.text((30,15),f'{i:02d} {label}',font=font,fill='#292929');tile.paste(im.resize((width,h),Image.Resampling.LANCZOS),(30,65));thumbs.append(tile)
 old=Image.open(V/f'delivery/{stem}.jpg').convert('RGB');pw=760;ph=round(im.height*pw/im.width);pair=Image.new('RGB',(1600,ph+90),'#f5f3ef');dr=ImageDraw.Draw(pair);dr.text((30,15),f'{i:02d} {label} ／ 前版 → Xレビュー版',font=font,fill='#292929');pair.paste(old.resize((pw,ph),Image.Resampling.LANCZOS),(30,65));pair.paste(im.resize((pw,ph),Image.Resampling.LANCZOS),(810,65));pairs.append(pair)
# Hero landscape first; no cropped photographs or empty grid cell.
hero=Image.open(D/'02_u2.jpg');hh=round(hero.height*1780/hero.width);rows=[max(thumbs[0].height,thumbs[2].height),max(thumbs[3].height,thumbs[4].height)]
sheet=Image.new('RGB',(1840,180+hh+sum(rows)),'#f5f3ef');dr=ImageDraw.Draw(sheet);dr.text((30,18),'参考例・原宿3LDK ／ X／レビュー版',font=font,fill='#292929');dr.text((30,64),'元の撮影写真5視点・共通配置・ラグなし',font=small,fill='#666666');dr.text((30,108),'02 リビングからダイニング',font=font,fill='#292929');sheet.paste(hero.resize((1780,hh),Image.Resampling.LANCZOS),(30,155));y=180+hh
for row,ids in enumerate([[0,2],[3,4]]):
 for col,k in enumerate(ids):sheet.paste(thumbs[k],(col*920,y))
 y+=rows[row]
sheet.save(D/'00_overview.jpg',quality=95,icc_profile=icc)
comparison=Image.new('RGB',(1600,sum(p.height for p in pairs)),'#f5f3ef');y=0
for p in pairs:comparison.paste(p,(0,y));y+=p.height
comparison.save(D/'06_revision_comparison.jpg',quality=95,icc_profile=icc)
living=Image.open(D/'01_u1.png');living.crop((0,1600,living.width,4500)).save(D/'08_u1_composed.jpg',quality=98,subsampling=0,icc_profile=icc)

for name in ['07_plan.png','layout.json','layout.diff','camera_fit_X.json','input_sha256.json']:
 shutil.copy2(O/name,D/name)
shutil.copy2(V/'delivery/speaker_layout.json',D/'speaker_layout.json')
manifest=json.loads((V/'delivery/model_sources.json').read_text(encoding='utf8'))
manifest.append({'revision':'X','geometry':'W repaired geometry unchanged; dining+6chairs moved as a rigid assembly','upholstery':'Sofa source material preserved in hue, seam AO and restrained leather-like micro-specular response added per X brief; not a newly confirmed upholstery selection','camera':'u2 and p13 refitted; source photo unchanged','lighting':'Original four lights unchanged; one180W estimated broad Eames ceiling/window return added'})
(D/'model_sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
for name in ['metrics_X.json','scene_delta_X.json','scene_inspection.json']:
 shutil.copy2(O/name,D/'details'/name)
(D/'details/material_trials').mkdir(exist_ok=True)
for name in ['p09_coat30.png','p09_rough_diffuse.png','sofa_variant_metrics.json']:
 shutil.copy2(O/'previews'/name,D/'details/material_trials'/name)
(D/'source').mkdir(exist_ok=True)
shutil.copy2(O/'Harajuku_LDK_X.blend',D/'source/Harajuku_LDK_X.blend')
(D/'source/README.txt').write_text('編集用の共通シーンと5カメラ。背景参照画像はパック済み。カメラを切り替える際はphoto_width/heightに解像度を合わせる。最終合成は別パスの反射・遮蔽・接地AO・粒状感処理を含むため、このblendだけの通常レンダーとは一致しない。解析用パス全量はZIPに含めていない。',encoding='utf8')
(D/'source/implementation').mkdir(exist_ok=True)
for name in ['prepare_X.py','render_X.py','calibrate_X.py','photo_floor_reflection_X.py','photo_contact_X.py','photo_composite_X.py','photo_common_X.py','photo_common_W.py','photo_common_V.py','photo_common_S.py','metrics_X.py','verify_scene_X.py','photo_inspect_X.py','photo_contacts_check_X.py','report_X.py']:
 shutil.copy2(R/name,D/'source/implementation'/name)
with (D/'source/README.txt').open('a',encoding='utf8') as sf:sf.write('\nimplementation/は計算ロジックの参照用コード。元の作業フォルダーとWの各視点シーン・中間パスを前提とするため、このZIPだけでそのまま実行する再現キットではありません。')
(D/'README.txt').write_text('参考例・原宿3LDK／試作CG X レビュー版\n\n01〜05：元写真全画角、原寸sRGB、同一合成のJPG/PNG。00一覧、06 W→X比較、07共通配置図、08 W版と同じ切り方のトリミング版。\nテーブルと椅子6脚のみ配置変更。床反射・既存反射の遮蔽・接触AOは全5視点で新規計算。元の撮影背景は生成・レタッチしていない。照明と床材、室寸法、カメラは写真・図面からの推定。\nカメラ誤差はu2:17.90px、p13:14.96px。目標7pxには未達。受け入れ完了としていない。全検証値・未達・判定不能項目はreport.mdを参照。\nsource/Harajuku_LDK_X.blendは編集用共通シーン。',encoding='utf8')
q=report;metrics=json.loads((O/'metrics_X.json').read_text())
for a,b in zip(q,metrics):a['X_measurements']=b
(D/'revision_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf8')
subprocess.run([sys.executable,str(R/'report_X.py')],check=True)
shutil.copy2(O/'report.md',D/'report.md')
shutil.copy2(O/'acceptance_results.json',D/'details/acceptance_results.json')
z=O/'Harajuku_3LDK_review_X.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as f:
 for p in sorted(D.rglob('*')):
  if p.is_file():f.write(p,p.relative_to(D))
with zipfile.ZipFile(z) as f:assert f.testzip() is None
print('X_REVIEW_PACKAGE_READY',z,z.stat().st_size,flush=True)
