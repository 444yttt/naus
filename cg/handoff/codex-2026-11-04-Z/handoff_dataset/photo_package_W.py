"""Publish the inspected W revision without overwriting V or its OneDrive link."""
from pathlib import Path
from PIL import Image,ImageCms,ImageDraw,ImageFont,ImageOps
import numpy as np,json,shutil,zipfile,hashlib
R=Path(__file__).resolve().parent;V=R/'out/photo_final_V';O=R/'out/photo_final_W';D=O/'delivery';D.mkdir(exist_ok=True)
icc=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
shots=['u1','u2','p09','p01','p13'];labels=['リビング・テレビ壁','リビングからダイニング','窓際からリビング','ダイニング','キッチン']
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',27);small=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',19)
report=[];thumbs=[];pairs=[]
import subprocess,sys
# Use the final common composite settings for every finished camera, including
# views completed before the last numerical occlusion correction.
for shot in shots:subprocess.run([sys.executable,str(R/'photo_composite_W.py'),shot,'full'],check=True)
subprocess.run([sys.executable,str(R/'photo_details_W.py')],check=True)
for i,(shot,label) in enumerate(zip(shots,labels),1):
 im=Image.open(O/f'{shot}_full_composite.png').convert('RGB');source=Image.open(R/f'images/photos_srgb/{shot}.png').convert('RGB')
 assert im.size==source.size,(shot,im.size,source.size)
 a=np.asarray(im)[::7,::7].astype('int16');b=np.asarray(source)[::7,::7].astype('int16');mask=np.asarray(Image.open(O/f'{shot}_effect_mask.png'))[::7,::7]
 err=int(np.abs(a-b)[mask==0].max()) if (mask==0).any() else 0
 assert err<=2,(shot,'untouched plate changed',err)
 stem=f'{i:02d}_{shot}';im.save(D/f'{stem}.jpg',quality=98,subsampling=0,icc_profile=icc);im.save(D/f'{stem}.png',icc_profile=icc)
 settings=json.loads((O/f'{shot}_refinement.json').read_text())
 for item in settings.get('mesh',[]):
  if item['object'].startswith('SEAT-FABRIC'):
   for key in list(item):
    if key not in ['object','original_vertices']:item.pop(key)
   item.update(surface_version=2,source_components=5,repair='interpolated visible pad envelopes; timber-covered rear skin omitted; fine relief simplified')
 report.append({'shot':shot,'native_dimensions':list(im.size),'unchanged_plate_max_error_8bit':err,'camera':'unchanged from V','render':settings,'grain':json.loads((O/f'{shot}_full_camera_grain.json').read_text()),'sha256':hashlib.sha256((D/f'{stem}.jpg').read_bytes()).hexdigest()})
 width=860;h=round(im.height*width/im.width);tile=Image.new('RGB',(920,h+90),'#f5f3ef');dr=ImageDraw.Draw(tile);dr.text((30,15),f'{i:02d} {label}',font=font,fill='#292929');tile.paste(im.resize((width,h),Image.Resampling.LANCZOS),(30,65));thumbs.append(tile)
 old=Image.open(V/f'delivery/{stem}.jpg').convert('RGB');pw=760;ph=round(im.height*pw/im.width);pair=Image.new('RGB',(1600,ph+90),'#f5f3ef');dr=ImageDraw.Draw(pair);dr.text((30,15),f'{i:02d} {label} ／ 前版 → 反射・接地修正',font=font,fill='#292929');pair.paste(old.resize((pw,ph),Image.Resampling.LANCZOS),(30,65));pair.paste(im.resize((pw,ph),Image.Resampling.LANCZOS),(810,65));pairs.append(pair)
# Hero landscape first; no cropped photographs or empty grid cell.
hero=Image.open(D/'02_u2.jpg');hh=round(hero.height*1780/hero.width);rows=[max(thumbs[0].height,thumbs[2].height),max(thumbs[3].height,thumbs[4].height)]
sheet=Image.new('RGB',(1840,180+hh+sum(rows)),'#f5f3ef');dr=ImageDraw.Draw(sheet);dr.text((30,18),'参考例・原宿3LDK ／ 反射・接地修正版 W',font=font,fill='#292929');dr.text((30,64),'元の撮影写真5視点・共通配置・ラグなし',font=small,fill='#666666');dr.text((30,108),'02 リビングからダイニング',font=font,fill='#292929');sheet.paste(hero.resize((1780,hh),Image.Resampling.LANCZOS),(30,155));y=180+hh
for row,ids in enumerate([[0,2],[3,4]]):
 for col,k in enumerate(ids):sheet.paste(thumbs[k],(col*920,y))
 y+=rows[row]
sheet.save(D/'00_overview.jpg',quality=95,icc_profile=icc)
comparison=Image.new('RGB',(1600,sum(p.height for p in pairs)),'#f5f3ef');y=0
for p in pairs:comparison.paste(p,(0,y));y+=p.height
comparison.save(D/'06_revision_comparison.jpg',quality=95,icc_profile=icc)
living=Image.open(D/'01_u1.png');living.crop((0,1600,living.width,4500)).save(D/'08_u1_composed.jpg',quality=98,subsampling=0,icc_profile=icc)
shutil.copy2(V/'delivery/07_plan.png',D/'07_plan.png')
for name in ['layout.json','speaker_layout.json']:
 shutil.copy2(V/'delivery'/name,D/name)
manifest=json.loads((V/'delivery/model_sources.json').read_text(encoding='utf8'))
for item in manifest:
 if 'eames' in item.get('item','').lower():
  if 'note' in item:item['note']=item['note'].replace('original geometry retained','original frame and floor glides retained; cushion revision documented below')
  item['W_surface_revision']='five original cushion component envelopes interpolated; concealed rear upholstery omitted under plywood; fine relief simplified; original frame and floor glides retained'
(D/'model_sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
(D/'details').mkdir(exist_ok=True)
shutil.copy2(V/'delivery/verification/camera_validation.json',D/'details/camera_fit_unchanged_from_V.json')
(D/'revision_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
(D/'README.txt').write_text('参考例・原宿3LDK ／ 試作CG 反射・接地修正版 W\n\n01〜05：全画角の原寸JPG・PNG（sRGB）。\n00：一覧、06：前版との比較、07：共通配置図。\n08：手前の椅子の見切れを避けた構図調整版（01の原寸からトリミング、引き伸ばしなし）。01も全画角で保管しています。\n床反射は実際の3D形状をCyclesで再計算し、既存反射の遮蔽、10cm以内の形状による接地AO、写真の床色を組み合わせています。床の反射率と照明は写真からの推定です。\nEamesは元の5つのクッションの各外形寸法を維持して開いた面と縁を修復。布と革はそれぞれの材質で調整しています。カメラ位置と家具の共通配置は前版を維持しています。\n全画角画像の撮影背景色や構図を変更せず、追加家具のみ周辺部の解像低下と微細な粒状感を調整しました。\nsource/に編集用Blenderデータを同梱。最終画像には別パスの反射・遮蔽・接地AOの合成を含みます。\n',encoding='utf8')
z=O/'Harajuku_3LDK_delivery_W.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as f:
 for p in sorted(D.rglob('*')):
  if p.is_file():f.write(p,p.relative_to(D))
with zipfile.ZipFile(z) as f:assert f.testzip() is None
print('W_PACKAGE_READY',z,z.stat().st_size,flush=True)
