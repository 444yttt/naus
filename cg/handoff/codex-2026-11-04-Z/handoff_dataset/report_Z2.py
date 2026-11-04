"""Audit the user's original22 checkboxes. Preserve failures and extra old gates.

Run only after all native renders and visual inspection. This never changes goal
status or treats a confirmation rate as measured photorealism.
"""
from pathlib import Path
import json,copy,hashlib
R=Path(__file__).resolve().parent;O=R/'out_Z2';D=O/'delivery';W=R/'out/photo_final_W'
def read(p):return json.loads(p.read_text(encoding='utf8'))
spec=(R/'instructions_X/ACCEPTANCE.md').read_text(encoding='utf8');requirements=[l[6:] for l in spec.splitlines() if l.startswith('- [ ] ')];assert len(requirements)==22
progress=read(O/'native_progress.json');assert progress['state']=='renders_complete' and len(progress['completed'])==5
m=read(O/'metrics_Z2.json');sc=read(O/'scene_delta_Z2.json');cam=read(O/'camera_fit_Z2.json');contacts=read(D/'details/contact_coverage.json');placement=read(R/'out_X/u2_placement_X.json');wi=read(W/'scene_inspection.json');visual=read(O/'visual_review_Z2.json');checks=[]
assert len(m)==5 and len(visual['views'])==5
for v in visual['views']:
    assert v['native_png_sha256']==hashlib.sha256((O/f"{v['shot']}_full_composite.png").read_bytes()).hexdigest(),'Visual review is stale'
def add(ok,evidence):
    i=len(checks);checks.append({'source_checkbox':i+1,'requirement':requirements[i],'result':'PASS' if ok is True else 'FAIL' if ok is False else 'UNVERIFIED','evidence':evidence})
def metric(shot):return next(v for v in m if v['shot']==shot)
add(0<=placement['after_gap_m']<=.004,{'before_gap_m':placement['before_gap_m'],'after_gap_m':placement['after_gap_m'],'rotation_delta_deg':placement['rotation_delta_deg'],'translation_after_rotation_m':placement['translation_after_rotation_m'],'basis':'Z source mesh poses equal X; unchanged architecture'})
add(all(not v['island_penetration'] and v['glazing_clearance_m']>.1 and v['room_right_clearance_m']>0 and v['room_bottom_clearance_m']>0 for v in placement['chair_checks']),placement['chair_checks'])
old=read(W/'delivery/layout.json');new=read(O/'layout.json')
def allowed(d):
    d=copy.deepcopy(d)
    for i in d['items']:
        if i['id']=='dining':i.pop('center');i.pop('angle')
    for i in d['chairs']['items']:i.pop('center');i.pop('angle')
    for k in ['enabled','status']:d['rug'].pop(k,None)
    return d
add(allowed(old)==allowed(new),{'latest_user_override':'ラグを追加。その他はテーブル＋椅子6脚だけ位置変更','diff_file':'layout.diff','rug_spec':'rug_specification.json'})
add((O/'07_plan.png').exists() and new['rug']['enabled'],{'plan':'07_plan.png','label':'model gap approximately2mm; old420mm line removed','rug':'earlier provisional4000x3500mm restored'})
joint={s:metric(s)['island_joint_AO'] for s in ['u2','p01','p13']};visible=[v for v in joint.values() if v['visible_sample_count']]
add(bool(visible) and all(v['shadow_present'] for v in visible),{'views':joint,'rule':'visible seam samples only; absence of visible samples is explicitly retained'})
e=metric('u2')['eames_floor'];ratio=e['Z']/max(e['reference_photo_dark_reflection_band_Y'],1e-9)
add(bool(e['Z']>e['W'] and .65<=ratio<=1.35),{'historical_mixed_reflection_shadow_ROI':e,'Z_to_photo_band_ratio':ratio,'warning':'This historical ROI is mostly dark-wood mirror reflection, not isolated cast shadow. Its conservative FAIL is retained.','isolated_diffuse_shadow_diagnostic':read(O/'shadow_audit/isolated_shadow_metrics.json')})
e=metric('u2')['eames_back'];add(bool(e['Z']['mean_Y']>e['W']['mean_Y'] and e['Z']['p95_p05_ratio']>1.2),e)
add(all(v['eames_cushion_sha256']==next(w for w in wi if w['shot']==v['shot'])['eames_cushion_geometry_sha256'] for v in sc),{'proof':'scene_delta_Z2.json versus W scene_inspection.json; actual repaired vertex-byte SHA256'})
add(all(metric(s)['sofa']['contrast_increase_pass'] for s in ['u1','p09']),{s:metric(s)['sofa'] for s in ['u1','p09']})
faces=[f for v in m if 'sofa' in v for f in v['sofa']['face_groups']];neg=[f['Z_CCT_proxy_K'] for f in faces if f['world_axis']==1 and f['sign']==-1];pos=[f['Z_CCT_proxy_K'] for f in faces if f['world_axis']==1 and f['sign']==1];warm=sum(neg)/len(neg) if neg else None;cool=sum(pos)/len(pos) if pos else None
add(bool(neg and pos and warm<cool),{'window_minus_Y_reflected_colour_CCT_proxy_K':warm,'room_plus_Y_reflected_colour_CCT_proxy_K':cool,'difference_K':cool-warm if neg and pos else None,'scope':'same normal-based diagnostic as X; includes internal cushion faces; not measured illuminant CCT'})
top=[f for f in metric('p09')['sofa']['face_groups'] if f['world_axis']==2 and f['sign']==1]
add(bool(top and top[0]['Z_green_excess_over_RB']>0),{'native_top_face':top,'definition':'weak positive G-(R+B)/2 in linear RGB; original specification asks weak visible green, not a mandatory increase over W; old increase test retained below'})
add(all(any(v['base_colour_linked'] and v['Coat Weight']>0 and v['AO_nodes'] for k,v in s['actual_materials'].items() if k.startswith('Shedir02')) for s in sc),{'materials':[{v['shot']:v['actual_materials']} for v in sc],'method':'3D material nodes; no local image retouch; original hue retained'})
fits=[v for v in cam if v['shot'] in ['u2','p13']]
add(all(v['Z_improves_original_observation_RMS_vs_W'] and v['Z_improves_refined_observation_RMS_vs_W'] for v in fits),{'camera_fit':fits,'target_7px':'NOT achieved; values and reasons explicitly recorded as required by the original conditional clause','reason':'Approximate unsurveyed architecture retains residuals. A sub7px lens fit was rejected because it curved independently straight photographed window edges.','independent_floor_validation':read(R/'out_Y/floor_direction_validation.json'),'lens_rejection':read(R/'out_Y/native_lens_edge_validation.json')})
covered=all(v['outside_floor_mask']==0 and v['contacts_on_exposed_floor']==v['exposed_floor_with_nearby_reflection'] for s in contacts for v in s['objects'].values());seen=any(v['contacts']>0 for s in contacts for v in s['objects'].values())
add(bool(covered and seen and all(v['contact_visual_pass'] for v in visual['views'])),{'contact_coverage':contacts,'visual_review':'visual_review_Z2.json','rug_rule':'opaque rug-covered feet require contact shadow rather than a floor mirror image; zero-candidate views require visual inspection'})
add(all(v['camera_max_numeric_difference']==0 for v in sc if v['shot'] not in ['u2','p13']),{v['shot']:v['camera_max_numeric_difference'] for v in sc})
floor=metric('p01')['floor_colour'];add(floor['far_mean_match_within_0_5'],{**floor,'qualification':'Historical0.5/255 threshold retained. This fixed ROI is affected by estimated shadow transport, so it does not prove an influence-free receiver; do not cherry-pick a better-matching region.'})
add(bool(floor['near_reflection_pixels']>0 and floor['near_Z_photo_mean_abs_difference_8bit']>.1),floor)
add(all(v['unchanged_plate_pass'] for v in m),{v['shot']:v['unchanged_plate_max_error_8bit'] for v in m})
add(all(v['grain_identical'] for v in m),{v['shot']:v['grain'] for v in m})
fresh=[]
for shot in ['u1','u2','p09','p01','p13']:
    for mode in ['furniture','opacity','environment','environment_occluded','white_reference']:
        p=O/f'{shot}_full_floor_reflection_{mode}_passes0001.exr';fresh.append({'file':p.name,'fresh':p.exists() and p.stat().st_mtime>=progress['started'],'bytes':p.stat().st_size if p.exists() else 0})
add(all(v['fresh'] and v['bytes']>0 for v in fresh) and all(v['reflection_visual_pass'] for v in visual['views']),{'fresh_occlusion_renders':fresh,'visual_review':'visual_review_Z2.json','method':'all-five new environment-before/after occlusion plus furniture/coverage/white-reference passes'})
expected=['00_overview.jpg','06_revision_comparison.jpg','07_plan.png','08_u1_composed.jpg']+[f'{i:02d}_{s}.{e}' for i,s in enumerate(['u1','u2','p09','p01','p13'],1) for e in ['jpg','png']];missing=[p for p in expected if not(D/p).exists()];add(not missing,{'missing':missing,'native_sizes':{v['shot']:v['native_dimensions'] for v in m}})
expected=['source/Harajuku_LDK_Z2.blend','revision_QA.json','report.md','README.txt'];missing=[p for p in expected if not(D/p).exists()];add(not missing,{'missing':missing,'revision_name':'Z preserves previous W/X files; original deliverable roles retained'})
assert len(checks)==22
(O/'acceptance_results.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')
count=sum(v['result']=='PASS' for v in checks);legacy={'u2_7px':next(v for v in fits if v['shot']=='u2')['target_7px_pass'],'p13_7px':next(v for v in fits if v['shot']=='p13')['target_7px_pass'],'top_green_increase_over_W':bool(top and top[0]['Z_green_excess_over_RB']>top[0]['W_green_excess_over_RB'])}
summary={'original_source_checkbox_count':22,'confirmed':count,'confirmation_rate':count/22,'not_a_photorealism_measurement':True,'legacy_extra_thresholds_preserved':legacy,'goal_completion_not_set_by_this_report':True};(O/'acceptance_summary.json').write_text(json.dumps(summary,indent=2))
lines=['# 参考例・原宿3LDK／試作CG Z2','',f'原仕様の22チェック行を単位とした確認結果：{count}/22。これは項目の確認率であり、物理的な再現精度を測定した百分率ではありません。','', 'Z2はZの共通シーンに2点だけ変更：①Eames座面の殻の後ろの開口から見えていたクッション下面の細片228面を除去、②コーヒーテーブル2台と背面一体テーブルの材質を木目の見える濃色オークに変更（「コーヒーテーブルの光が微妙」への対応）。カメラ・照明・配置・ラグはZと同一で、全5視点を原寸で再レンダー。最新の追加指示に従いShindo Naturalを復帰。家具の共通配置を保ち、5視点の家具・反射・遮蔽・接地を原寸から再計算。新規4写真は部屋構造の参考とし、合成背景は元の5写真です。','', '照明と床材、室寸法、カメラは写真と図面に基づく推定です。カメラ7px目標の未達、床の固定ROI、Eamesの反射と影の区別は以下に残しています。元の受け入れ条件はdetails/acceptance_source.mdを参照。','', '|元仕様の行|結果|根拠|','|---|---|---|']
for v in checks:lines.append(f"|{v['source_checkbox']}. {v['requirement'].replace('|','/')}|{v['result']}|{json.dumps(v['evidence'],ensure_ascii=False).replace('|','/')}|")
lines+=['','## 元仕様外の追加確認','', 'コーヒーテーブルの前面2枚の天板のみを抽出した輝度・白飛び（W/X/Z/Z2、同じカメラ・同じ形状マスク）：','```json',json.dumps(read(O/'coffee_quality.json'),ensure_ascii=False,indent=2),'```','', 'ラグの不透明な内側に元の床反射が透けないこと：','```json',json.dumps(read(O/'rug_composite_check.json'),ensure_ascii=False,indent=2),'```','', '旧スクリプトの追加閾値も省略せず記録：','```json',json.dumps(legacy,ensure_ascii=False,indent=2),'```','', '原仕様の「7px以下」は未達時に値と理由を記録する条項を含みます。上表ではRMS低下と記録を判定し、7px達成とは表記していません。緑の色被りは元仕様どおり弱い正の値を判定し、旧スクリプト独自の「Wより増加」も別に残しています。','', '## Wからの配置差分','```diff',(O/'layout.diff').read_text(encoding='utf8'),'```']
(O/'report.md').write_text('\n'.join(lines),encoding='utf8');print('Z2_REPORT_GENERATED_NO_COMPLETION_CLAIM',summary,flush=True)
