"""Assemble inspected native artifacts. Run manually after the acceptance audit.

This does not assign a score, declare success, upload, or replace old deliveries.
"""
from pathlib import Path
import json,shutil,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageCms
R=Path(__file__).resolve().parent;O=R/'out_Z';D=O/'delivery';W=R/'out/photo_final_W'
shots=['u1','u2','p09','p01','p13'];labels=['リビング・テレビ壁','リビングからダイニング','窓際からリビング','ダイニング','キッチン']
progress=json.loads((O/'native_progress.json').read_text())
assert progress['state']=='renders_complete' and set(progress['completed'])==set(shots)
assert (O/'VALIDATION_READY.txt').exists()
assert (O/'report.md').exists(),'Create factual acceptance report before assembly'
metrics=json.loads((O/'metrics_Z.json').read_text());assert len(metrics)==5
assert all(r['unchanged_plate_pass'] and r['grain_identical'] for r in metrics)
assert len({r['rug_sha256'] for r in json.loads((O/'rug_invariants.json').read_text())})==1
D.mkdir(exist_ok=True);(D/'details').mkdir(exist_ok=True);(D/'source/implementation').mkdir(parents=True,exist_ok=True)
icc=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes();font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',27);small=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',19)
tiles=[];pairs=[];qa=[]
for i,(shot,label) in enumerate(zip(shots,labels),1):
    im=Image.open(O/f'{shot}_full_composite.png').convert('RGB');plate=Image.open(R/f'images/photos_srgb/{shot}.png')
    assert im.size==plate.size
    stem=f'{i:02d}_{shot}';im.save(D/f'{stem}.png',icc_profile=icc);im.save(D/f'{stem}.jpg',quality=98,subsampling=0,icc_profile=icc)
    w=860;h=round(im.height*w/im.width);tile=Image.new('RGB',(920,h+90),'#f5f3ef');ImageDraw.Draw(tile).text((30,15),f'{i:02d} {label}',font=font,fill='#292929');tile.paste(im.resize((w,h),Image.Resampling.LANCZOS),(30,65));tiles.append(tile)
    old=Image.open(W/f'{shot}_full_composite.png').convert('RGB');w=760;h=round(im.height*w/im.width);pair=Image.new('RGB',(1600,h+90),'#f5f3ef');ImageDraw.Draw(pair).text((30,15),f'{i:02d} {label} ／ W → Z',font=font,fill='#292929');pair.paste(old.resize((w,h),Image.Resampling.LANCZOS),(30,65));pair.paste(im.resize((w,h),Image.Resampling.LANCZOS),(810,65));pairs.append(pair)
    qa.append({'shot':shot,'revision':'Z','native_dimensions':list(im.size),'camera':json.loads((O/f'{shot}_camera.json').read_text()),'measurements':next(r for r in metrics if r['shot']==shot),'render':{'foreground_percentage':100,'foreground_samples':24,'reflection_percentage':50,'reflection_samples':[48,40,48,48,8],'fresh_all_passes':True},'png_sha256':hashlib.sha256((D/f'{stem}.png').read_bytes()).hexdigest()})
hero=Image.open(D/'02_u2.jpg');hh=round(hero.height*1780/hero.width);heights=[max(tiles[0].height,tiles[2].height),max(tiles[3].height,tiles[4].height)];sheet=Image.new('RGB',(1840,180+hh+sum(heights)),'#f5f3ef');dr=ImageDraw.Draw(sheet);dr.text((30,18),'参考例・原宿3LDK ／ 試作CG Z',font=font,fill='#292929');dr.text((30,64),'元の撮影写真5視点・共通配置・Shindo Natural',font=small,fill='#666666');dr.text((30,108),'02 リビングからダイニング',font=font,fill='#292929');sheet.paste(hero.resize((1780,hh),Image.Resampling.LANCZOS),(30,155));y=180+hh
for row,ids in enumerate([[0,2],[3,4]]):
    for col,k in enumerate(ids):sheet.paste(tiles[k],(col*920,y))
    y+=heights[row]
sheet.save(D/'00_overview.jpg',quality=95,icc_profile=icc)
sheet=Image.new('RGB',(1600,sum(p.height for p in pairs)),'#f5f3ef');y=0
for p in pairs:sheet.paste(p,(0,y));y+=p.height
sheet.save(D/'06_revision_comparison.jpg',quality=95,icc_profile=icc)
Image.open(D/'01_u1.png').crop((0,1600,4284,4500)).save(D/'08_u1_composed.jpg',quality=98,subsampling=0,icc_profile=icc)
for name in ['07_plan.png','layout.json','layout.diff','report.md','rug_specification.json','camera_fit_Z.json']:
    shutil.copy2(O/name,D/name)
for name in ['metrics_Z.json','scene_delta_Z.json','scene_inspection.json','rug_invariants.json','rug_composite_check.json','camera_projection_consistency.json','acceptance_results.json','input_audit_Z.json']:
    assert (O/name).exists(),name
    shutil.copy2(O/name,D/'details'/name)
for name in ['acceptance_summary.json','visual_review_Z.json','coffee_quality.json','chosen_candidate_invariants.json']:
    shutil.copy2(O/name,D/'details'/name)
shutil.copy2(R/'instructions_X/ACCEPTANCE.md',D/'details/acceptance_source.md')
for name in ['floor_direction_validation.json','native_lens_edge_validation.json','native_edge_camera_u2.json','native_edge_camera_p13.json']:
    shutil.copy2(R/'out_Y'/name,D/'details'/name)
shutil.copy2(O/'shadow_audit/isolated_shadow_metrics.json',D/'details/isolated_shadow_metrics.json')
shutil.copy2(W/'delivery/speaker_layout.json',D/'speaker_layout.json')
manifest=json.loads((W/'delivery/model_sources.json').read_text(encoding='utf8'));manifest.append({'revision':'Z','changes':'approved dining rigid assembly, common estimated return lighting and material refinement, u2/p13 native-edge camera refit, restored Shindo','rug':json.loads((O/'rug_specification.json').read_text()),'photographs':'original five sRGB photos, not generated replacement','geometry':'W repaired Eames retained, existing furniture poses exact X'})
(D/'model_sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
(D/'revision_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')
shutil.copy2(O/'Harajuku_LDK_Z.blend',D/'source/Harajuku_LDK_Z.blend')
for name in ['prepare_Z.py','add_rug_Z.py','render_Z.py','photo_floor_reflection_Z.py','photo_contact_Z.py','photo_composite_Z.py','transform_reflection_Z.py','reflection_display_transform_Z.py','photo_common_X.py','photo_common_W.py','photo_common_V.py','photo_common_S.py','verify_rug_Z.py','photo_contacts_check_Z.py','camera_projection_consistency_Z.py','calibrate_u2_native_conservative_Y.py','calibrate_native_edges_Y.py']:
    shutil.copy2(R/name,D/'source/implementation'/name)
(D/'README.txt').write_text('参考例・原宿3LDK／試作CG Z\n\n01〜05：元の撮影写真の全画角・原寸sRGB、同じ合成から作成したJPG/PNG。00一覧、06 W→Z比較、07共通配置図、08 Wと同じ範囲のトリミング版。\nShindo Naturalを以前の仮寸法4000×3500mmで追加。家具本体の共通配置を維持。全5視点の家具・背景基準・床反射・既存反射の遮蔽・接触影を新規に計算。\n照明・床材・室内寸法・カメラは写真と図面からの推定。建築の合わせ込み誤差、検証結果と残る制約はreport.mdを参照。\nsource/には背景と仕上げ画像をパックした編集用共通シーンと5カメラを収録。\n',encoding='utf8')
(D/'source/README.txt').write_text('共通シーン＋5カメラ。カメラ切替時はphoto_width/heightへ解像度を合わせる。\n最終画像は別計算の反射・遮蔽・接触AO・粒状感を含むため、blendの通常レンダーだけでは一致しない。implementation/は計算ロジックの参照コードであり、元作業フォルダー、Xの各視点シーンと中間パスを前提とする。ZIPだけで実行可能な再現キットではない。\nShindoの形状は寸法ベースの試作、色は公式仕上げ画像参照。メーカー配布3Dではない。\n',encoding='utf8')
print('Z_ARTIFACTS_ASSEMBLED_NO_UPLOAD_NO_COMPLETION_CLAIM',flush=True)
