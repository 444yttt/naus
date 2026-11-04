# 原宿3LDK 試作CG X／レビュー用

**受け入れ完了ではありません。** カメラの7px目標に未達です。以下のFAIL・判定不能を残したままレビューへ渡します。元背景の生成置換・画像レタッチは行っていません。

未達／判定待ち：2-1 Eames足元の暗さ=FAIL、3-1 p09 ソファ面平均の輝度差=FAIL、3-2 窓側と日陰側の色味=FAIL、4-1 u2 カメラRMS改善／7px目標=FAIL、4-1 p13 カメラRMS改善／7px目標=FAIL、5-1 p01家具から離れた床の色=FAIL
反射分離の弱フィット時は、BRDF白基準からの既存反射推定を較正分岐の下限と同じ係数（3.0、0.18〜0.72）へ統一しました。旧弱フィット分岐だけ3.8、0.22〜0.78となり、相関の閾値を跨ぐと床が過暗になる不連続がありました。幾何学的な反射coverage・既存反射の遮蔽率は減らしていません。画像上の局所塗り直しはしていません。
## 変更内容
テーブル中心 [3.815999984741211, 5.089000225067139, 0.0] → [3.909625291824341, 5.4999003410339355, 0.0]m。回転0.375362°。回転後の平行移動[0.0936252623796463, 0.4108999967575073]m。椅子6脚はテーブルに対する相対配置を保持。窓から離す追加補正0mm。その他家具は位置・向きを変更していません。

元の4ライトは不変。Eamesへの180W・直径2.4mの推定回り込み光を全5シーンに同条件で追加。背面木部の拡散応答とソファの材質を調整。p01の床反射材だけSpecular/Coat Tint=(1,.96,.86)を適用。床の反射率・照明・室寸法は写真と図面に基づく推定です。

## 受け入れ検証

| 項目 | 結果 | 根拠・数値 |
|---|---|---|
| 1-1 テーブル短辺とアイランド端面 | PASS | ソースメッシュの投影外形：417.315 → 2.000mm。端面に正対する角度へ0.375362°回転。長さ2600mm・幅1150mm不変。 |
| 1-2 めり込み／椅子6脚の建築干渉 | PASS | 椅子の凸包と固定島形状：侵入0。ガラス面まで最小480.7mm、島まで最小295.1mm。窓枠専用実測モデルなし。クリアランスにより図面上の枠位置からも離れている。 |
| 1-3 layout.jsonはテーブルと椅子6脚のみ変更 | PASS | layout.diff（全文を本書末尾に掲載）とscene_delta_X.json。その他家具の姿勢変化0。 |
| 1-4 配置図更新／旧420mm注記削除 | PASS | 07_plan.pngを元図から再作成。旧赤線と420mm注記を削除し、モデル上約2mmと表記。 |
| 1-5 u2 接合部の接触AO | PASS | {"visible_sample_count": 20, "normalized_AO_values": [0.5223897099494934, 0.6187297701835632, 0.7927327752113342, 0.9471967816352844, 0.5289224982261658, 0.6291349530220032, 0.7933844923973083, 0.943140983581543, 0.5420334935188293, 0.6199086308479309, 0.7891476154327393, 0.9416654706001282, 0.5232974886894226, 0.6120885014533997, 0.7890189290046692, 0.9415022730827332, 0.5379602313041687, 0.6244707107543945, 0.7973280549049377, 0.9354732632637024], "minimum_ratio": 0.5223897099494934, "shadow_present": true, "visibility_note": "Island face samples immediately above tabletop, ray-tested against foreground geometry; null means seam samples are outside frame or occluded, not a failed pixel measurement."} |
| 1-5 p01 接合部の接触AO | N/A（可視サンプルなし） | {"visible_sample_count": 0, "normalized_AO_values": [], "minimum_ratio": null, "shadow_present": null, "visibility_note": "Island face samples immediately above tabletop, ray-tested against foreground geometry; null means seam samples are outside frame or occluded, not a failed pixel measurement."} |
| 1-5 p13 接合部の接触AO | PASS | {"visible_sample_count": 20, "normalized_AO_values": [0.536744236946106, 0.6253869533538818, 0.7989246845245361, 0.9462278485298157, 0.5359938144683838, 0.6190553903579712, 0.8066778182983398, 0.9462544322013855, 0.5337134003639221, 0.6226385831832886, 0.796742856502533, 0.9493486285209656, 0.5311078429222107, 0.6179155707359314, 0.7982086539268494, 0.9490229487419128, 0.5228016376495361, 0.6187297701835632, 0.803746223449707, 0.948371410369873], "minimum_ratio": 0.5228016376495361, "shadow_present": true, "visibility_note": "Island face samples immediately above tabletop, ray-tested against foreground geometry; null means seam samples are outside frame or occluded, not a failed pixel measurement."} |
| 2-1 Eames足元の暗さ | FAIL | {"W": 0.12066932022571564, "X": 0.0832781121134758, "photo_same_pixels": 0.218765527009964, "reference_photo_dark_reflection_band_Y": 0.04234929382801056, "samples": 223821, "reference_samples": 33740, "region_normalized": [0.09, 0.6, 0.3, 0.82], "method": "common rendered reflection coverage in Eames floor ROI excluding foreground. Reference is photographed dark window-reflection band, not an independently measured cast shadow."} X/写真の参照反射帯=1.966。参照帯は窓の反射であり、照度や同一形状の影の実測ではない。 |
| 2-2 Eames背面の明暗と回り込み | PASS | {"W": {"sample_pixels": 200190, "mean_Y": 0.0062047382816672325, "min_Y": 0.0012539307354018092, "max_Y": 0.04131735861301422, "max_min_ratio": 32.95027160644531, "p95_p05_ratio": 3.261212110519409, "bbox": [[773, 2241], [1345, 2779]], "selection": "projected preserved wood-shell bounds, eroded brown-chroma pixels; camera-specific masks; luminance linear-sRGB, not illuminance"}, "X": {"sample_pixels": 219315, "mean_Y": 0.011204896494746208, "min_Y": 0.0014710131799802184, "max_Y": 0.07989981770515442, "max_min_ratio": 54.31618118286133, "p95_p05_ratio": 2.732656478881836, "bbox": [[714, 2239], [1286, 2788]], "selection": "projected preserved wood-shell bounds, eroded brown-chroma pixels; camera-specific masks; luminance linear-sRGB, not illuminance"}} |
| 2-3 W補修サーフェス維持 | PASS | 全5シーンの補修済み頂点バイト列SHA256がWと一致。元フレーム・グライドも姿勢不変。 |
| 3-1 u1 ソファ面平均の輝度差 | PASS | 面平均Yの標準偏差 W=0.115583、X=0.119777。各面の値は下表・metrics_X.json。 |
| 3-1 p09 ソファ面平均の輝度差 | FAIL | 面平均Yの標準偏差 W=0.104290、X=0.102322。各面の値は下表・metrics_X.json。 |
| 3-2 窓側と日陰側の色味 | FAIL | 窓側(-Y)の反射色からの参考CCT=5691.9K、反対側(+Y)=5487.5K、差=-204.4K。材色と反射を含む近似であり、入射光の測定色温度ではない。 |
| 3-3 p09上面の緑の色被り | PASS | [{"world_axis": 2, "sign": 1, "samples": 51809, "W_mean_Y": 0.35397765040397644, "X_mean_Y": 0.3446698486804962, "W_mean_RGB_linear": [0.35799723863601685, 0.355206698179245, 0.32972046732902527], "X_mean_RGB_linear": [0.3498735725879669, 0.34573203325271606, 0.31862345337867737], "X_red_blue_ratio": 1.0980784893035889, "W_red_blue_ratio": 1.0857598781585693, "X_green_excess_over_RB": 0.011483520269393921, "W_green_excess_over_RB": 0.011347860097885132, "W_CCT_proxy_K": 6181.547493367255, "X_CCT_proxy_K": 6141.4913704895525}] 緑指標=G-(R+B)/2、線形RGB。面平均には座面と背クッション上縁が含まれる。 |
| 3-4 縫い目・微細な反射を3D材質で調整 | PASS | 元の明色を維持。局所AO距離75mm、混合0.58、Roughness0.46、Coat0.13/Roughness0.32、微細Bump距離0.35mm・Strength0.30。画像レタッチは使用していない。元の布材に革調の微細反射を追加した仕様。 |
| 4-1 u2 カメラRMS改善／7px目標 | FAIL | 原寸RMS 21.02924 → 17.90382px、最大26.97279px。目標7pxは未達。11基準点を削除せず固定し、位置・回転・焦点距離・主点を再最適化。主点移動は幅±2.5%以内。固定した図面読取形状と観測点が単一カメラで整合しないため。 |
| 4-1 p13 カメラRMS改善／7px目標 | FAIL | 原寸RMS 16.78106 → 14.96457px、最大37.35757px。目標7pxは未達。11基準点を削除せず固定し、位置・回転・焦点距離・主点を再最適化。主点移動は幅±2.5%以内。固定した図面読取形状と観測点が単一カメラで整合しないため。 |
| 4-2 脚元の床受け・反射カバレッジ | PASS | [{"u1": {"contacts": 72, "outside_floor_mask": 0, "with_nearby_reflection": 72}}, {"u2": {"contacts": 122, "outside_floor_mask": 0, "with_nearby_reflection": 122}}, {"p09": {"contacts": 246, "outside_floor_mask": 0, "with_nearby_reflection": 246}}, {"p01": {"contacts": 47, "outside_floor_mask": 0, "with_nearby_reflection": 47}}, {"p13": {"contacts": 0, "outside_floor_mask": 0, "with_nearby_reflection": 0}}] p13など可視脚元候補が0の場合は遮蔽・画角による。独立した位置精度の測定ではない。 |
| 4-3 他3視点のカメラ不変 | PASS | [{"u1": 0.0}, {"u2": 1.438638687133789}, {"p09": 0.0}, {"p01": 0.0}, {"p13": 0.27371788024902344}] |
| 5-1 p01家具から離れた床の色 | FAIL | {"far_ROI_normalized": [0.02, 0.82, 0.25, 0.98], "sample_pixels": 256386, "mean_RGB_8bit": {"photo": [113.19543188785659, 159.80156482803272, 197.55961323941244], "W": [110.24875383211251, 155.87390887177926, 192.37467334409834], "X": [111.56394654934357, 157.5844897927344, 194.3843345580492]}, "X_minus_photo_RGB_8bit": [-1.6314853385130164, -2.217075035298336, -3.1752786813632383], "far_mean_match_within_0_5": false, "near_reflection_pixels": 972331, "near_X_photo_mean_abs_difference_8bit": 50.95586825199786, "X_blue_excess_B_minus_R_delta": -1.543793342850222, "note": "Fixed far-floor ROI excludes foreground and reflected geometry with101px dilation; rendered shadow/indirect-light influence is not excluded, so this ROI cannot independently establish absence of furniture influence. Full mean differences are retained rather than selecting pixels by image agreement. Actual source plate itself unchanged."} 選択ROIは家具本体・反射を除外していますが、影・間接光・サンプリング差を除外できていません。家具の影響がないことの独立検証も未達です。出力の色一致を基準に領域を選び直してはいません。 |
| 5-2 p01家具近くの反射維持 | PASS | 実形状の反射カバレッジ>0.216の床画素=972331。同画素でXと写真の平均絶対差=50.956/255。 |
| 共通 未加工領域の誤差2/255以内 | PASS | [{"u1": 1}, {"u2": 1}, {"p09": 1}, {"p01": 1}, {"p13": 2}] PNGとsRGB変換済み元写真の全未加工画素を比較。JPGは同一合成の別エンコード。 |
| 共通 粒状感・周辺にじみ | PASS | [{"u1": 0.74128981330432}, {"u2": 0.6500000087544322}, {"p09": 1.2500000442378223}, {"p01": 0.74128981330432}, {"p13": 0.741301093949005}] 最小0.65/255。周辺にじみはWと同じpremultiplied alpha処理。 |
| 共通 全5視点新規レンダーと反射遮蔽更新 | PASS | foreground原寸100%、反射50%、サンプル24/48（W同等）。全5視点のforeground・背景基準・反射5パス・接地AOを再計算。Wの部分レンダーは使っていない。空の天井域は家具レンダー対象外だが、原写真の全画角で合成。 |
| 入力／W原本を上書きしない | PASS | 20入力のSHA256を再照合。提供された期待ハッシュ値はなし。前回の手元W納品ZIPと同梱source、元作業シーン、今回の指示ZIP・展開仕様書を記録。 |
| 出力一式 | PASS | 実ファイルの存在確認。欠落=[]。本report.mdはこの処理末尾で生成。ZIPのCRCは作成後に別途全件確認。 |

## ソファの面ごとの実測画像値

線形sRGBの輝度Y。Normalパスで面方向を区分し、材質IDで布部分のみ選び、縁を侵食して比較。画素は原寸の2px間隔。参考CCTは反射材色込みのMcCamy近似で、照明の測定値ではありません。

|視点|世界法線|画素数|W平均Y|X平均Y|W参考CCT K|X参考CCT K|X線形RGB|
|---|---|---:|---:|---:|---:|---:|---|
|u1|X -1|149197|0.386263|0.401622|6177.7|6142.2|[0.4088819622993469, 0.40243226289749146, 0.3723979592323303]|
|u1|Y -1|1781|0.165748|0.161207|5821.7|5691.9|[0.17157837748527527, 0.16066467761993408, 0.136039599776268]|
|u1|Y +1|3316|0.141194|0.136818|5560.5|5459.5|[0.14980588853359222, 0.13570985198020935, 0.10954832285642624]|
|u1|Z +1|16156|0.381661|0.372487|6257.3|6209.1|[0.37666645646095276, 0.37358349561691284, 0.3495330214500427]|
|p09|X +1|53886|0.176466|0.167035|5829.8|5817.0|[0.1743307262659073, 0.16720856726169586, 0.14388294517993927]|
|p09|Y +1|17375|0.106127|0.102725|5542.5|5515.5|[0.11094305664300919, 0.10230984538793564, 0.08260725438594818]|
|p09|Z +1|51809|0.353978|0.344670|6181.5|6141.5|[0.3498735725879669, 0.34573203325271606, 0.31862345337867737]|

## 入力SHA256

```json
{
  "C:\\Users\\akaay\\Documents\\Codex\\2026-11-03\\codex-3d\\handoff_dataset\\out\\photo_final_W\\Harajuku_3LDK_delivery_W.zip": "6099918b831954e914a71f85557b1cbb9d6f7900db6d24dd2c750346579f6068",
  "C:\\Users\\akaay\\Documents\\Codex\\2026-11-03\\codex-3d\\handoff_dataset\\out\\photo_final_W\\delivery\\source\\Harajuku_LDK_W.blend": "5923ad4e37a5015530ca4046925212ca69a71b30783bcdd5468ca1245dcdf5ea",
  "handoff_dataset\\out\\photo_final_W\\u1_photo_scene.blend": "d065c57c6eb360ab7ee7e33fc9087d488dc0d8d55495581cf350acb001f41b33",
  "handoff_dataset\\out\\photo_final_W\\u2_photo_scene.blend": "ce503b612bc3bdebc3302ecc1ef6ebff0afb03b3ef4d1d9bc339b16a02818d2e",
  "handoff_dataset\\out\\photo_final_W\\p09_photo_scene.blend": "62036c078b75b883e2fed68b897ffed17d37b1cae1cf606019d6f51e850242f2",
  "handoff_dataset\\out\\photo_final_W\\p01_photo_scene.blend": "0684f6e5e194f68f03f57b8c4911bf66d7d46a6d9f21de1c37938d6330f95d7c",
  "handoff_dataset\\out\\photo_final_W\\p13_photo_scene.blend": "748f49f60af9a629870162c270c1cdb72b86656e724ed3ee3e1b3466a6d5f634",
  "handoff_dataset\\images\\photos_srgb\\u1.png": "d1eb2e42ccb1a2c0388c48c8941b43b2af650dca776bd38e83164097f7abf41c",
  "handoff_dataset\\images\\photos_srgb\\u2.png": "59a2f323e507781805d0d489f6bcc4ca565ef13e9e47577febb353099b02cd2f",
  "handoff_dataset\\images\\photos_srgb\\p09.png": "6ad4d62dc58f0a171313f443df13affac7f2e6e75790aabdc4ae52632fc24cc5",
  "handoff_dataset\\images\\photos_srgb\\p01.png": "668f48f223e593783c9c88012c446a2864b64fd5ac89f395c7438d283747c081",
  "handoff_dataset\\images\\photos_srgb\\p13.png": "771e6ba251f1e6d6777293dab627265d41bc4746d7e336cb9155ac288af9ce78",
  "handoff_dataset\\out\\photo_final_W\\delivery\\layout.json": "c8d82c6caab4859506d498e9946edaf6a8f719b0687a9562543fb15d2979d97b",
  "handoff_dataset\\out\\photo_final_W\\delivery\\details\\camera_fit_unchanged_from_V.json": "318da17200d17e05b21052acfd66c052b4e707d4d91f9520e545134d4fee9ab1",
  "C:\\Users\\akaay\\.codex\\codex-remote-attachments\\01a19f51-138e-7622-817c-433434a14e62\\8456A875-0C48-4B57-AFB9-AF4BD2FA5D60\\1-codex_pack.zip": "574016100051c8d26a34254c1ffca055293688fe11d337cab48b7e65b3e1af1d",
  "handoff_dataset\\instructions_X\\00_user_instructions.md": "850ece16a4e79a375a3db8ed57e0fb981470606438352e831d860ca2a6131dcd",
  "handoff_dataset\\instructions_X\\ACCEPTANCE.md": "29e9f7a1cd17240218e5780c85c805d2d1646a00ae69089e49e1801d0d4745b8",
  "handoff_dataset\\instructions_X\\AGENTS.md": "bd6abde47a1496a4857af28ae74982c29c48cce0d36211d4fb565aa65a392ff2",
  "handoff_dataset\\instructions_X\\GOAL_PROMPT.md": "eea385693da0a7412211eb7166367c7d4ced82103d2736a23a00c5684ce13fd3",
  "handoff_dataset\\instructions_X\\REVIEW_HANDOFF.md": "b66c75335034817155b7ef1c8ca5d17d80bdcacf059306af61e00492be52ed56"
}
```

## layout.json 差分

```diff
--- W/layout.json
+++ X/layout.json
@@ -14,14 +14,14 @@
     {
       "id": "dining",
       "center": [
-        3.816,
-        5.089
+        3.909625291824341,
+        5.4999003410339355
       ],
       "size": [
         2.6,
         1.15
       ],
-      "angle": 70.7,
+      "angle": 71.07536019894142,
       "product_selection_status": "user confirmed",
       "brand": "Minotti",
       "model": "Linha Dining",
@@ -3492,74 +3492,74 @@
     "items": [
       {
         "center": [
-          4.4080786464082475,
-          3.9810433778945242
+          4.508949751899237,
+          4.39584612662504
         ],
         "size": [
           0.692,
           0.66
         ],
-        "angle": 70.7,
+        "angle": 71.07536176046575,
         "side_sign": -1
       },
       {
         "center": [
-          4.6890158802144875,
-          4.783274186740269
+          4.784625340897437,
+          5.1999002103970815
         ],
         "size": [
           0.692,
           0.66
         ],
-        "angle": 70.7,
+        "angle": 71.07536176046575,
         "side_sign": -1
       },
       {
         "center": [
-          4.969953114020727,
-          5.585504995586014
+          5.060300929895635,
+          6.003954294169122
         ],
         "size": [
           0.692,
           0.66
         ],
-        "angle": 70.7,
+        "angle": 71.07536176046575,
         "side_sign": -1
       },
       {
         "center": [
-          2.662046885979273,
-          4.592495004413987
+          2.758949687218913,
+          4.995845937974061
         ],
         "size": [
           0.692,
           0.66
         ],
-        "angle": 70.7,
+        "angle": 71.07536176046575,
         "side_sign": 1
       },
       {
         "center": [
-          2.9429841197855127,
-          5.394725813259732
+          3.0346252762171115,
+          5.799900021746102
         ],
         "size": [
           0.692,
           0.66
         ],
-        "angle": 70.7,
+        "angle": 71.07536176046575,
         "side_sign": 1
       },
       {
         "center": [
-          3.2239213535917526,
-          6.196956622105477
+          3.3103008652153103,
+          6.6039541055181425
         ],
         "size": [
           0.692,
           0.66
         ],
-        "angle": 70.7,
+        "angle": 71.07536176046575,
         "side_sign": 1
       }
     ],

```

## 未対応の観察

固定した図面読取形状のため、再校正後も建築の基準点誤差が残ります。画面端の見切れは家具を視点別に移動せず、08の構図調整版を併記しました。
p09の材質追加比較（25%原寸プレビュー）では、Coat0.30案の面平均Y標準偏差0.10146、Diffuse Roughness0.35案0.09463に対し、同じ画素群のW参照は0.10436でした。どちらも採用していません。画像と数値はdetails/material_trials/に収録。現行X設定より差が減る結果でした。