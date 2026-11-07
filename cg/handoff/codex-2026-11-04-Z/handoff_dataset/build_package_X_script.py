from pathlib import Path
R=Path(__file__).resolve().parent
text=(R/'photo_package_W.py').read_text(encoding='utf8').split("shutil.copy2(V/'delivery/07_plan.png'")[0]
text=text.replace("V=R/'out/photo_final_V';O=R/'out/photo_final_W'","V=R/'out/photo_final_W';O=R/'out_X'").replace('photo_composite_W','photo_composite_X').replace('photo_details_W','photo_details_X')
text=text.replace("settings=json.loads((O/f'{shot}_refinement.json').read_text())","settings={'revision':'X','baseline_W':json.loads((V/f'{shot}_refinement.json').read_text()),'changes':['table+6chairs rigid assembly','Eames broad return light and wood response','sofa local seam AO and micro-specular','u2/p13 bounded pinhole refit','p01 floor specular tint'],'geometry':'W repaired Eames surface unchanged','samples':24,'foreground_resolution_percent':100,'reflection_resolution_percent':50}")
text=text.replace("'camera':'unchanged from V'","'camera':('refitted from W' if shot in ['u2','p13'] else 'unchanged from W')")
text=text.replace('反射・接地修正版 W','X／レビュー版').replace('反射・接地修正','Xレビュー版')
text+='''
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
with (D/'source/README.txt').open('a',encoding='utf8') as sf:sf.write('\\nimplementation/は計算ロジックの参照用コード。元の作業フォルダーとWの各視点シーン・中間パスを前提とするため、このZIPだけでそのまま実行する再現キットではありません。')
(D/'README.txt').write_text('参考例・原宿3LDK／試作CG X レビュー版\\n\\n01〜05：元写真全画角、原寸sRGB、同一合成のJPG/PNG。00一覧、06 W→X比較、07共通配置図、08 W版と同じ切り方のトリミング版。\\nテーブルと椅子6脚のみ配置変更。床反射・既存反射の遮蔽・接触AOは全5視点で新規計算。元の撮影背景は生成・レタッチしていない。照明と床材、室寸法、カメラは写真・図面からの推定。\\nカメラ誤差はu2:17.90px、p13:14.96px。目標7pxには未達。受け入れ完了としていない。全検証値・未達・判定不能項目はreport.mdを参照。\\nsource/Harajuku_LDK_X.blendは編集用共通シーン。',encoding='utf8')
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
'''
(R/'package_X.py').write_text(text,encoding='utf8')
