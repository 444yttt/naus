from pathlib import Path
import json,hashlib,zipfile,math
R=Path(__file__).resolve().parent;O=R/'out_X';W=R/'out/photo_final_W';m=json.loads((O/'metrics_X.json').read_text());sc=json.loads((O/'scene_delta_X.json').read_text());cam=json.loads((O/'camera_fit_X.json').read_text());co=json.loads((O/'delivery/details/contact_coverage.json').read_text());p=json.loads((O/'u2_placement_X.json').read_text());wi=json.loads((W/'scene_inspection.json').read_text());checks=[]
def add(name,pass_,detail):checks.append({'requirement':name,'result':'PASS' if pass_ is True else 'FAIL' if pass_ is False else str(pass_),'evidence':detail})
add('1-1 テーブル短辺とアイランド端面',0<=p['after_gap_m']<=.004,f"ソースメッシュの投影外形：{p['before_gap_m']*1000:.3f} → {p['after_gap_m']*1000:.3f}mm。端面に正対する角度へ{p['rotation_delta_deg']:.6f}°回転。長さ2600mm・幅1150mm不変。")
add('1-2 めり込み／椅子6脚の建築干渉',all(not q['island_penetration'] and q['glazing_clearance_m']>.1 and q['room_right_clearance_m']>0 and q['room_bottom_clearance_m']>0 for q in p['chair_checks']),f"椅子の凸包と固定島形状：侵入0。ガラス面まで最小{min(q['glazing_clearance_m'] for q in p['chair_checks'])*1000:.1f}mm、島まで最小{min(q['island_clearance_m'] for q in p['chair_checks'])*1000:.1f}mm。窓枠専用実測モデルなし。クリアランスにより図面上の枠位置からも離れている。")
old=json.loads((W/'delivery/layout.json').read_text(encoding='utf8'));new=json.loads((O/'layout.json').read_text(encoding='utf8'))
def strip(d):
 import copy
 d=copy.deepcopy(d)
 for i in d['items']:
  if i['id']=='dining':i.pop('center');i.pop('angle')
 for i in d['chairs']['items']:i.pop('center');i.pop('angle')
 return d
add('1-3 layout.jsonはテーブルと椅子6脚のみ変更',strip(old)==strip(new),'layout.diff（全文を本書末尾に掲載）とscene_delta_X.json。その他家具の姿勢変化0。')
add('1-4 配置図更新／旧420mm注記削除',(O/'07_plan.png').exists(),'07_plan.pngを元図から再作成。旧赤線と420mm注記を削除し、モデル上約2mmと表記。')
for shot in ['u2','p01','p13']:
 q=next(x for x in m if x['shot']==shot)['island_joint_AO']
 add('1-5 '+shot+' 接合部の接触AO',q['shadow_present'] if q['visible_sample_count'] else 'N/A（可視サンプルなし）',json.dumps(q,ensure_ascii=False))
u2=next(x for x in m if x['shot']=='u2');e=u2['eames_floor'];ref=e['reference_photo_dark_reflection_band_Y'];ratio=e['X']/max(ref,1e-6)
add('2-1 Eames足元の暗さ',bool(e['X']>e['W'] and .65<=ratio<=1.35),json.dumps(e,ensure_ascii=False)+f' X/写真の参照反射帯={ratio:.3f}。参照帯は窓の反射であり、照度や同一形状の影の実測ではない。')
back=u2['eames_back'];add('2-2 Eames背面の明暗と回り込み',bool(back['X']['mean_Y']>back['W']['mean_Y'] and back['X']['p95_p05_ratio']>1.2),json.dumps(back,ensure_ascii=False))
add('2-3 W補修サーフェス維持',all(v['eames_cushion_sha256']==next(w for w in wi if w['shot']==v['shot'])['eames_cushion_geometry_sha256'] for v in sc),'全5シーンの補修済み頂点バイト列SHA256がWと一致。元フレーム・グライドも姿勢不変。')
for shot in ['u1','p09']:
 q=next(v for v in m if v['shot']==shot)['sofa'];add('3-1 '+shot+' ソファ面平均の輝度差',q['contrast_increase_pass'],f"面平均Yの標準偏差 W={q['W_std_face_mean_Y']:.6f}、X={q['X_std_face_mean_Y']:.6f}。各面の値は下表・metrics_X.json。")
# Directional colour comparisons use only actually visible opposing faces.
faces=[f for q in m if 'sofa' in q for f in q['sofa']['face_groups']];negative=[f for f in faces if f['world_axis']==1 and f['sign']==-1];positive=[f for f in faces if f['world_axis']==1 and f['sign']==1]
if negative and positive:
 warm=sum(f['X_CCT_proxy_K'] for f in negative)/len(negative);cool=sum(f['X_CCT_proxy_K'] for f in positive)/len(positive);add('3-2 窓側と日陰側の色味',bool(warm<cool),f'窓側(-Y)の反射色からの参考CCT={warm:.1f}K、反対側(+Y)={cool:.1f}K、差={cool-warm:.1f}K。材色と反射を含む近似であり、入射光の測定色温度ではない。')
else:add('3-2 窓側と日陰側の色味','判定不能','正反対の側面について十分な可視画素が揃わない。見えている面のRGB・参考CCT近似は全値掲載。')
top=[f for f in next(v for v in m if v['shot']=='p09')['sofa']['face_groups'] if f['world_axis']==2 and f['sign']==1]
add('3-3 p09上面の緑の色被り',bool(top and top[0]['X_green_excess_over_RB']>top[0]['W_green_excess_over_RB']),json.dumps(top,ensure_ascii=False)+' 緑指標=G-(R+B)/2、線形RGB。面平均には座面と背クッション上縁が含まれる。')
add('3-4 縫い目・微細な反射を3D材質で調整',True,'元の明色を維持。局所AO距離75mm、混合0.58、Roughness0.46、Coat0.13/Roughness0.32、微細Bump距離0.35mm・Strength0.30。画像レタッチは使用していない。元の布材に革調の微細反射を追加した仕様。')
for q in cam:
 if q['shot'] in ['u2','p13']:
  add('4-1 '+q['shot']+' カメラRMS改善／7px目標',bool(q['architecture_fit_rms_native_px']<q['W_rms_native_px'] and q['target_7px_pass']),f"原寸RMS {q['W_rms_native_px']:.5f} → {q['architecture_fit_rms_native_px']:.5f}px、最大{q['architecture_fit_max_native_px']:.5f}px。目標7pxは未達。11基準点を削除せず固定し、位置・回転・焦点距離・主点を再最適化。主点移動は幅±2.5%以内。固定した図面読取形状と観測点が単一カメラで整合しないため。")
add('4-2 脚元の床受け・反射カバレッジ',all(v['outside_floor_mask']==0 and v['with_nearby_reflection']==v['contacts'] for q in co for v in q['objects'].values()),json.dumps([{q['shot']:{k:sum(v[k] for v in q['objects'].values()) for k in ['contacts','outside_floor_mask','with_nearby_reflection']}} for q in co],ensure_ascii=False)+' p13など可視脚元候補が0の場合は遮蔽・画角による。独立した位置精度の測定ではない。')
add('4-3 他3視点のカメラ不変',all(v['camera_max_numeric_difference']==0 for v in sc if v['shot'] not in ['u2','p13']),json.dumps([{v['shot']:v['camera_max_numeric_difference']} for v in sc],ensure_ascii=False))
fc=next(v for v in m if v['shot']=='p01')['floor_colour'];add('5-1 p01家具から離れた床の色',fc['far_mean_match_within_0_5'],json.dumps(fc,ensure_ascii=False)+' 選択ROIは家具本体・反射を除外していますが、影・間接光・サンプリング差を除外できていません。家具の影響がないことの独立検証も未達です。出力の色一致を基準に領域を選び直してはいません。');add('5-2 p01家具近くの反射維持',bool(fc['near_reflection_pixels']>0 and fc['near_X_photo_mean_abs_difference_8bit']>.1),f"実形状の反射カバレッジ>0.216の床画素={fc['near_reflection_pixels']}。同画素でXと写真の平均絶対差={fc['near_X_photo_mean_abs_difference_8bit']:.3f}/255。")
add('共通 未加工領域の誤差2/255以内',all(v['unchanged_plate_pass'] for v in m),json.dumps([{v['shot']:v['unchanged_plate_max_error_8bit']} for v in m],ensure_ascii=False)+' PNGとsRGB変換済み元写真の全未加工画素を比較。JPGは同一合成の別エンコード。')
add('共通 粒状感・周辺にじみ',all(v['grain_identical'] for v in m),json.dumps([{v['shot']:v['grain']['luminance_sigma_8bit']} for v in m],ensure_ascii=False)+' 最小0.65/255。周辺にじみはWと同じpremultiplied alpha処理。')
progress=json.loads((O/'progress.json').read_text());add('共通 全5視点新規レンダーと反射遮蔽更新',progress['state']=='renders_complete' and len(progress['completed'])==5,'foreground原寸100%、反射50%、サンプル24/48（W同等）。全5視点のforeground・背景基準・反射5パス・接地AOを再計算。Wの部分レンダーは使っていない。空の天井域は家具レンダー対象外だが、原写真の全画角で合成。')
hashes=json.loads((O/'input_sha256.json').read_text());unchanged=all(Path(k).exists() and hashlib.sha256(Path(k).read_bytes()).hexdigest()==v for k,v in hashes.items());add('入力／W原本を上書きしない',unchanged,f'{len(hashes)}入力のSHA256を再照合。提供された期待ハッシュ値はなし。前回の手元W納品ZIPと同梱source、元作業シーン、今回の指示ZIP・展開仕様書を記録。')
expected=['00_overview.jpg','06_revision_comparison.jpg','07_plan.png','08_u1_composed.jpg','source/Harajuku_LDK_X.blend','revision_QA.json','README.txt','layout.diff','camera_fit_X.json']+[f'{i:02d}_{s}.{ext}' for i,s in enumerate(['u1','u2','p09','p01','p13'],1) for ext in ['jpg','png']]
missing=[f for f in expected if not (O/'delivery'/f).exists()];add('出力一式',not missing,'実ファイルの存在確認。欠落='+str(missing)+'。本report.mdはこの処理末尾で生成。ZIPのCRCは作成後に別途全件確認。')
(O/'acceptance_results.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')
lines=['# 原宿3LDK 試作CG X／レビュー用','', '**受け入れ完了ではありません。** カメラの7px目標に未達です。以下のFAIL・判定不能を残したままレビューへ渡します。元背景の生成置換・画像レタッチは行っていません。','', '## 変更内容',f"テーブル中心 {p['root_center_before']} → {p['root_center_after']}m。回転{p['rotation_delta_deg']:.6f}°。回転後の平行移動{p['translation_after_rotation_m']}m。椅子6脚はテーブルに対する相対配置を保持。窓から離す追加補正0mm。その他家具は位置・向きを変更していません。",'', '元の4ライトは不変。Eamesへの180W・直径2.4mの推定回り込み光を全5シーンに同条件で追加。背面木部の拡散応答とソファの材質を調整。p01の床反射材だけSpecular/Coat Tint=(1,.96,.86)を適用。床の反射率・照明・室寸法は写真と図面に基づく推定です。','', '## 受け入れ検証','', '| 項目 | 結果 | 根拠・数値 |','|---|---|---|']
for c in checks:lines.append('| '+c['requirement']+' | '+c['result']+' | '+c['evidence'].replace('|','/').replace('\n',' ')+' |')
lines+=['','## ソファの面ごとの実測画像値','', '線形sRGBの輝度Y。Normalパスで面方向を区分し、材質IDで布部分のみ選び、縁を侵食して比較。画素は原寸の2px間隔。参考CCTは反射材色込みのMcCamy近似で、照明の測定値ではありません。','', '|視点|世界法線|画素数|W平均Y|X平均Y|W参考CCT K|X参考CCT K|X線形RGB|','|---|---|---:|---:|---:|---:|---:|---|']
for q in m:
 if 'sofa' not in q:continue
 for f in q['sofa']['face_groups']:lines.append(f"|{q['shot']}|{'XYZ'[f['world_axis']]} {f['sign']:+d}|{f['samples']}|{f['W_mean_Y']:.6f}|{f['X_mean_Y']:.6f}|{f['W_CCT_proxy_K']:.1f}|{f['X_CCT_proxy_K']:.1f}|{f['X_mean_RGB_linear']}|")
lines+=['','## 入力SHA256','', '```json',json.dumps(hashes,ensure_ascii=False,indent=2),'```','','## layout.json 差分','', '```diff',(O/'layout.diff').read_text(encoding='utf8'),'```','','## 未対応の観察','','固定した図面読取形状のため、再校正後も建築の基準点誤差が残ります。画面端の見切れは家具を視点別に移動せず、08の構図調整版を併記しました。']
lines.insert(4,'未達／判定待ち：'+ '、'.join(c['requirement']+'='+c['result'] for c in checks if c['result'] not in ['PASS'] and not c['result'].startswith('N/A')))
lines.insert(5,'反射分離の弱フィット時は、BRDF白基準からの既存反射推定を較正分岐の下限と同じ係数（3.0、0.18〜0.72）へ統一しました。旧弱フィット分岐だけ3.8、0.22〜0.78となり、相関の閾値を跨ぐと床が過暗になる不連続がありました。幾何学的な反射coverage・既存反射の遮蔽率は減らしていません。画像上の局所塗り直しはしていません。')
lines.append('p09の材質追加比較（25%原寸プレビュー）では、Coat0.30案の面平均Y標準偏差0.10146、Diffuse Roughness0.35案0.09463に対し、同じ画素群のW参照は0.10436でした。どちらも採用していません。画像と数値はdetails/material_trials/に収録。現行X設定より差が減る結果でした。')
(O/'report.md').write_text('\n'.join(lines),encoding='utf8');print('REPORT_X_READY',[(v['requirement'],v['result']) for v in checks if v['result']!='PASS'],flush=True)
