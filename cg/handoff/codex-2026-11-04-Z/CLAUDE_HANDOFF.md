# 原宿3LDK・実写合成CG — Claudeへの全面引き継ぎ

作成日: 2026-11-04 JST。最新のユーザー指示は「全部Claudeに引き継ぐ。途中経過と今後の予定、仕様家具とモデルなど要件全てをまとめて」。このためCodexのレンダー・検証待機・継続処理を停止し、旧作業ゴールを一時停止した。**完成・90%以上達成とは報告していない。**

## 1. 最初に見るもの

| 内容 | パス（このファイルからの相対） |
|---|---|
| Claudeに渡す短い開始指示 | `CLAUDE_START_HERE.md` |
| 最新共通シーン、5カメラ、背景画像入り | `handoff_dataset/out_Z/Harajuku_LDK_Z.blend` |
| 最新配置図・配置データ | `handoff_dataset/out_Z/07_plan.png`、`layout.json`、`layout.diff` |
| 最新の原寸合成3枚 | `out_Z/p09_full_composite.png`、`u1_full_composite.png`、`u2_full_composite.png`（先頭に `handoff_dataset/`） |
| 同じ内容のJPEG | 上記の拡張子 `.jpg` |
| 途中経過・停止地点 | `handoff_dataset/out_Z/native_progress.json`、`WORK_STATUS_Z.md` |
| 元の具体的指示・受け入れ条件 | `handoff_dataset/instructions_X/00_user_instructions.md`、`ACCEPTANCE.md`、`AGENTS.md`、`GOAL_PROMPT.md`、`REVIEW_HANDOFF.md` |
| モデルの旧出典一覧 | `handoff_dataset/out/photo_final_W/delivery/model_sources.json`（ラグを含まないため本書を併用） |
| 旧W比較画像・検証 | `handoff_dataset/out/photo_final_W/` |
| 旧Xの全検証・失敗記録 | `handoff_dataset/out_X/` |

`out_Z/delivery/` には拡大確認画像が一部あるが、完成納品フォルダーではない。最終report、一覧、比較、ZIP等はまだ揃っていない。編集用masterは引き継ぎ時に作成済み。単独レンダーでは、別工程の反射合成・遮蔽等まで再現されない。

## 2. 目的・指示の優先順位

- 実際に撮影した部屋写真に選定家具を入れ、「本物が置かれた」と感じる試作CGにする。ピッチ動画・スライド等に使う想定。表記は「参考例・試作CG」。実績・実測済み確定プランと見せない。
- リビング中心の **5視点** が現在の作業範囲。最初のbriefには寝室1枚も別枠であるが、今回のW→X→Z改修には含めていない。寝室の古い画像を現在の成果と混ぜない。
- 画像全体に整合した合成を行う。家具のある部分だけ自然でも、床・建具・反射・遮蔽が破綻すれば不十分。
- 床目地、天井、窓枠、建具、アイランドなど確実な構造を基準にカメラと床面を合わせる。写真ごとの目分量配置は禁止。
- 1つの共通平面配置を全5カメラへ投影する。家具は視点ごとに動かさない。
- 現在許可された家具移動は **Linhaテーブル＋Torii6脚をアイランドに詰める変更**。他の家具の位置・向きはWと同一。最新のラグ追加はユーザーが明示した例外として追加済み。
- カメラ変更を許可されたのは **u2・p13だけ**。u1・p09・p01はWと同一に維持。
- 背景は元の写真。生成画像への置換・補修・背景レタッチで誤差を隠すことは禁止。写真全体の色合わせも行わない。CGの材質・照明・物理パス・合成で調整する。
- 部分レンダーの使い回しは禁止。同じシーン変更を採用したら全5視点を再レンダーする。W/Xは比較用に残す。
- 原寸sRGB、JPG/PNGを同じ合成内容で出す。PNGが画素検証の基準。JPEGは圧縮差がある。
- ユーザーの最新の品質要求は「これまでの条件90%以上まで必ず続ける」、特に「コーヒーテーブルの光が微妙」。**達成率を客観認定したものはまだない。** 今回はユーザー自身の全面引き継ぎ指示で停止した。
- 既存指示書には「Codex実装、Claudeレビュー」とあるが、最新指示でClaudeへ全面引き継ぎ。古い役割分担を理由に作業を止めない。
- 合成精度・変更・検証に絞って報告する。権利・予算・サイト・配置の是非などの意見は不要。
- 実測について質問済みで、ユーザーは「実測値はないので現資料で進める」と回答。再度それを待って止まらない。

古い `SPEC.md`、`LAYOUT_FACTS.md`、`MODEL_SOURCES.md`、元の `INTENT_3D_BRIEF.md` は履歴資料。BoConcept中心、B&Oテレビ65型、240cmダイニングなどは後の会話で変更済み。本書と後述の実データ・最新指示を優先する。

## 3. 最新の家具仕様・モデル・未確定事項

寸法はmm。実寸確認済み商品と、CGの近似・仮仕様を区別する。

| 用途 | 現在の採用・CG仕様 | データと確度 |
|---|---|---|
| ダイニング | **Minotti Linha “Dining” 2600×1150×740**。Grigio Orobico天板、脚Golden Brown。長辺を斜めFIX側に沿わせ、キッチン側短辺をアイランドへ詰める | 第三者の3300モデルを2600へ調整。公式2600 CADそのものではない。薄い側板厚を維持 |
| ダイニングチェア | **Minotti Torii系6脚**。窓側3・室内側3。明るいグレー布、脚はLinhaと全く同じGolden Brownマテリアル | ユーザー指定Warehouse SKP。モデル外形 **692×660×877**。メーカー公式Dining型・Standard/Large・回転機構との完全一致は未認証。初期「回転なし」の後で「固定じゃなくていいや」と発言があるため、固定を絶対条件としない |
| ソファ | **Poliform Ernest**。幅約3600、窓側カウチ奥行1700。反対側は座面＋背面一体テーブルの組み合わせ。TV背後の掘り込み幅より少し小さく納める意図 | 販売店配布FBXを正式モジュール外形に概ね合わせたもの。XY約1〜2%調整、背面テーブル再構築。現CGは淡い **Shedir 02 Burro** の見た目参考。実物貼り地の測色・最終SKU確定ではない |
| ソファ前テーブル | **Poliform Ernest 1200×900＋1200×700**。凹部同士を合わせる、画像指定のパズル状・段違い配置 | 販売店配布FBXの切欠き付きモデルを採用。CGはダークウッド。900角との組み合わせではない。黒木脚＋チタニウム天板案／全ダークウッド案が会話にある。現在は全体ダークウッドの試作材質で、工場仕様コードまでは未確定 |
| ラウンジ | **Eames Lounge Chair Classic 1脚**、窓向き。オットマンなし | Herman Miller公式SKPを変換。明るい革＋濃色木部は仮色。Wで座面等のジャギーを補修。Owen等の以前のPoliform案は不採用 |
| ラウンジテーブル | **Roche Bobois IVRESSE Ø600×H550**、白カララ天板、黒台座 | 技術資料・写真からの再構築。公式3Dデータではない。サイズは氷・ウイスキー・グラスを置ける程度、高さを確保した選択 |
| TV | **97型クラス**、16:9画面約2148×1208、壁掛け。中心高さ1150、下端約546 | 寸法ベースの試作形状。LG OLED evo G6の83型を示した後で「97型クラスへ拡大・取り付け高さを下げる」と変更。97型の確定型番・筐体は未確認 |
| TV背面壁 | ナチュラル系・グレージュ系のタイル処理 | 既存壁の形状に沿う試作仕上げ。TV裏だけ貧相にしない意図 |
| TV左右 | **B&O Beolab 28ペア**、**Charcoal Stain×Black Anthracite** | 公式OBJ。仕上げは再現材。左右をTVから同距離に配置済み。以前の偏った配置は修正対象だった |
| キッチン | **B&O Beosound Balance**、カウンターの細くなる先端側 | 公式OBJ。色は未指定でCGは仮グレー |
| リビングラグ | **Poliform Shindo Natural**、現仮サイズ4000×3500 | 最新ユーザー「やっぱりラグあった方がいいから追加」で復活。前の左右方向拡張案の矩形を復元。標準品サイズと確定したものではない。公式仕上げ画像＋寸法ベース自作メッシュ |

「白い家具が平面的」というレビューで“革”と書かれているが、Ernestの現設定は布の見た目参考。微細反射・縫い目・陰影を改善する要求であり、無断で革張り製品へ変更しない。

価格は今回の合成精度改修では再集計・確定していない。元の参考題「原宿3LDK・予算1500万円」は会話にあるが、現在の最終見積確定額として使わない。以前の別仕様価格を仮資料に使う許可はあったものの、確定型番と価格が揃った新見積は本作業で作っていない。

### 入手済みモデルの場所・出典

全て `handoff_dataset/` 以下。`models/` のテクスチャ・MTL・inspectionも維持する。元データは残し、既に加工した形状は最新blendにある。

| 対象 | ローカル元データ | 出典 |
|---|---|---|
| Ernestソファ | `models/ernest_sofa_mesmetric/Poliform-ERNEST-sofa.fbx` | https://mesmetric.com/en/modular/35938-ernest.html |
| Ernestテーブル | `models/ernest_tables_mesmetric/3d/Poliform-ERNEST-coffeetable-1.fbx`、同SKP | https://mesmetric.com/en/other/35943-ernest.html |
| Linha | `models/linha_warehouse/extracted/model.dae` と同フォルダー画像 | https://3dwarehouse.sketchup.com/model/5c6e68ad-e323-452e-b19f-bb94ddd2aaad/Minotti-Linha-Dining-table （作者Nikhil G.） |
| Torii | `models/torii_user_warehouse/source.skp`、`extracted/model.dae` | https://3dwarehouse.sketchup.com/model/d8bb7e13-a21f-456b-855e-796e4aa4c55f/MINOTTI-TORII-CHAIR （作者Maria Jose V.） |
| Eames | `models/eames_official/HMI_Eames_Lounge_Chair_Classic.skp` | https://www.hermanmiller.com/resources/3d-models-and-planning-tools/product-models/individual/eames-lounge-chair-classic/ |
| Beolab 28 | `models/beolab28/Beolab 28/obj/` のfloor woofer、tube、wooden curtain等 | https://support.bang-olufsen.com/hc/en-us/articles/360020100498-Beolab-28 |
| Balance | `models/balance/beosound_balance.obj` | https://support.bang-olufsen.com/hc/en-us/articles/360041238491-Beosound-Balance |
| IVRESSE | 形状はblend内。技術資料URL | https://technicals.roche-bobois.com/M66231103/TSv_IVRESSE_2017(2).pdf |
| Shindo | `out_Z/Shindo_Natural_official_reference.jpg`、`Shindo_official_dimensions.svg`、`add_rug_Z.py` | https://www.poliform.it/en/products/shindo/ |

Shindo画像元: https://s3.poliform.it/2025/07/Poliform_tappeti_SHINDO_finiture_1300x1740px_natural.jpg 。公式2022資料では標準3000×4000の表記があるため、現4000×3500を公式標準寸法と言わない。

ユーザーはモデル取得について、ログインを許可し、実際にログインした履歴あり。後に「無料の配布データだけで進める」を明示。有料Owenの購入等をしない。アカウントのパスワード・セッションは引き継ぎファイルに含めない。再取得を始めるより手元のモデルを使う。

## 4. 写真・カメラ・座標系

| 納品順 | ID | 原寸 | 状態 |
|---|---|---|---|
| 01 | u1 | 4284×5712 | 最新Z合成出力・個別数値検証・原寸目視済み |
| 02 | u2 | 5712×4284 | 最新Z合成出力済み、最終数値集計・目視は未実施 |
| 03 | p09 | 3024×4032 | 最新Z合成出力・個別数値検証・原寸目視済み |
| 04 | p01 | 3174×4233 | 原寸前景レンダーの途中で停止。部分出力を完成扱いしない |
| 05 | p13 | 3024×4032 | 最新シーン・カメラ準備済み、最新原寸パス未レンダー |

背景の基準は `images/photos_srgb/{ID}.png`（元写真をICC→sRGB変換）。元JPEGは `images/photos/`。新規の明るい4枚は **部屋構造の参考専用** とユーザーが訂正済み。仕上げの背景をその4枚へ勝手に差し替えない。間取り図は `images/plan/floorplan_large.jpg`、位置指定 `redbox.jpg`。図面はラスタ・概算で、実測寸法ではない。

単位m、Z上向き、床Z=0。原点はバルコニーガラス線と斜めFIX線の鋭角コーナー。+Xはバルコニー沿い、+Yは室内側。TV壁は概ねX=9.40。斜めFIX方向は旧概算70.7°。床板幅150mm等も仮定。最新版の実カメラ値は `out_Z/{ID}_camera.json` を使い、初期 `calib/` の数値をそのまま再採用しない。

### 主な共通配置

- Linha中心: X=3.909625292、Y=5.499900341。角度71.075360199°。Wから約X+93.6mm、Y+410.9mm、回転+0.375361761°。椅子6脚はテーブルに対する相対配置を維持。
- 短辺対アイランドの詳細形状計算: 417.315mm→**1.999867mm**（`out_X/u2_placement_X.json`）。ラスタ平面輪郭による別計算 `out_Z/clearance_Z.json` は **3.514282mm**。異なる近似輪郭の測定であり、混同しない。いずれも実測値ではない。
- 配置時の椅子対ガラス最小約480.7mm、対アイランド約295.1mm。形状の非貫通と椅子を引く使用時クリアランスは別。勝手に通路を新設する意図ではない。
- ソファ本体基準中心約[6.07,2.35]。主座面のX=5.565〜6.575、Y=.55〜3.25。反対端座面X=5.925〜6.615、Y=3.25〜4.15。窓側延長X=6.575〜7.265、Y=.55〜1.45。一体テーブルX=5.565〜5.925、Y=3.275〜4.125。
- Ernest前テーブル1: X=7.23〜8.13、Y=2.2〜3.4。テーブル2: X=7.63〜8.33、Y=1.6〜2.8。約600mm縦・400mm横オフセット、凹部の公称隙間20mm、外形全体1800×1100。画像指定の凹部パズル配置を維持。
- TV中心[9.345,2.35,1.15]。Beolab左右[9.05,.80,0]と[9.05,3.90,0]。TVのY=2.35からそれぞれ±1.55m、左右間3100mm。同じ壁離れでソファ側[6.3,2.35]へ約29.407°内振り。
- Eames中心付近[1.9,1.85]、1脚窓向き。Wの修復形状・原フレーム・脚端を維持。
- Balance[5.2,9.9,.91]付近。
- ラグ: X=5.2〜8.7、Y=.35〜4.35。図面上の左右拡張、上下方向は元の範囲を維持する意図。家具はラグ追加によって動かしていない。

厳密なオブジェクト単位の数値は `layout.json`、各blend、`scene_delta_Z.json`。テキストの丸め値からレイアウトを再構築しない。

## 5. ここまでの経緯と最新版

1. 初期は簡易家具と概算カメラ。ユーザーが遠近・床法線・共通配置の不整合を指摘。
2. 家具を現在のハイブランド構成へ順次変更。無料で入手できた公式・販売店・第三者モデルを導入。Eamesクッションの荒い段差はWで修復。
3. Wは5枚の一式を作成。ユーザー／レビューでEames、ソファ、2/5枚目カメラ、4枚目の青み、アイランドとの距離が残課題。
4. Xはテーブルをアイランドへ詰め、材質・カメラ等を改修して一式作成。ただし旧reportの26項目中19 PASS・6 FAIL・1 N/Aで、ユーザーは未達で止めることを拒否。Xを完成達成扱いしない。
5. Yは回り込み・カメラ・反射の表示変換などを試行。途中でユーザーがラグ復活を依頼し、Yを中断。
6. ZでShindoを戻し全5視点を新レンダー。初期Sheen .10・sky300Wはp09のソファ陰影がWより弱く、不採用。複数試行を経て現在のSheen .45・sky800W・warm200Wを選択。
7. **現在の選定値でp09・u1・u2の3視点の原寸合成が出た。p01前景の途中でClaude引き継ぎ指示を受け停止。p13未レンダー。** u2は停止直前に完成しており、2視点検証ファイルにはまだ反映されていない。

古いXのファイルをZとして扱わない。Zの初期試行、縮小プレビュー、Yの未完パスも最新の完成原寸ではない。`WORK_STATUS_Z.md` は追記履歴なので末尾の採用値を優先する。

### 最新Zの採用設定

- 元のXライトとWorldは変更せず、全視点共通の推定反射光を2灯追加。`Sunlit_balcony_floor_return_Y`: 200W、RGB(1,.72,.32)、矩形9×.6m、位置(4.7,-.10,.22)、照準(4.7,2,.60)。`Diagonal_sky_bay_return_Y`: **800W**、RGB(.65,.82,1)、矩形3×2.2m、位置(1.55,4.54,1.45)、法線(.937,-.349,0)。両方specular=0、glossy不可。視点限定のごまかしライトではない。
- `Shedir02_Burro_colour_study`: Sheen=.45、roughness=.46、coat=.13、coat rough=.32、AO距離25mm／mix .35、微細bump距離.00035m／strength .30。基色・元テクスチャ維持。
- `Ernest_dark_wood_study`: roughness=.22（X .32）、coat=.20（X 0）、coat rough=.16、bump距離.00012m（X .001）。基色維持。MatIndex10は前テーブルと背面一体テーブルで共有。
- ラグは公式Natural画像を未改変使用。厚み上端4.8mm、3〜4mmパイル参考、150mm縁の光学的櫛目。古い16mmの盛り上がった縞ではない。脚下は浅い圧縮面で追従。クロス物理ではない。各視点1枚、同形状SHA `e241d2fd8ee5368d5cc5c063fbbd0f0008d1da99c244d3a1cf442671b3426b18`。
- 床BRDFはroughness .10、coat .24／coat rough .09、IOR1.5。p01のCG反射色は(1,.96,.86)。反射・遮蔽の補正パスを別にレンダー。
- 反射の表示変換を修正。旧Xでは前景AgXと反射Reinhardが不整合。Zは線形EXRの非premult反射を、前景と同じAgX Medium High Contrast／露出−1.5で変換し、display-linearへ戻してopacity合成。
- 粒状感、半径依存のpremult境界にじみはWと同じ。原寸前景24spp、背景50%・8spp、床反射50%・各48/40/48/48/8spp、接地AO50%・24/8spp。**出力は原寸だが全補助パスまで原寸サンプルではない。**

このライティングは実測HDR・照度・光源単位の完全測光ではなく、写真からの推定。推定を「完全物理再現」と呼ばない。

## 6. 現在の検証結果（範囲を限定する）

`native_completed_metrics_Z.json`、`early_native_colour.json`、`rug_composite_check.json`、`coffee_quality.json`、`visual_review_Z.json` が根拠。これらは主にp09/u1の2枚まで。u2を確認済みと誤読しない。

- ソファ面平均輝度の標準偏差: **p09 W .104290→Z .107773、u1 W約.11558→Z .123196**。同カメラ・材質ID・法線群による比較では増加。
- その2枚の未加工写真領域の最大誤差 **1/255**、基準2/255以下。粒状感設定Wと同じ。
- 法線群からの反射色CCT指標では窓向き側5869K・室内側5924K、差約54K。**光源を測った色温度ではない**。クッション内側の面も含まれる色指標。
- p09座面上の弱い緑: linear G−(R+B)/2が+.00978。Wより増えたという条件ではなく、弱い緑があるという元条件。旧自作検査の「W以上に増やす」とは区別。
- ラグ内部の遮蔽検査: p09約243244画素・u1約49705画素でalpha=1。原床の透けなし。光学的にじみ・grain・量子化込みで期待値と比較済み。
- p09コーヒーテーブル上面: 線形輝度p05/.5/p95=.008149/.016743/.094040、標準偏差.030608（W .008371）、チャンネル飽和0。材質ID10だけでは背面テーブルも拾うので、**Normal Zと前テーブルworld bboxを併用**。数値が良くてもユーザーの光の不満が完全解消したとは未認定。
- `delivery/details/p09_coffee_W_Z_native.jpg` は同じ原寸の比較、`p09_Eames_contact_native.png` と `u1_contact_native.png` は接地確認用。p09全体と拡大、u1全体と拡大を内部目視済み。
- `visual_review_Z.json` はCodex内部の2視点のSHA紐付き記録。**Claude外部レビュー済みではない**。
- 元家具形状・ポーズと元ライト維持、他3カメラ差分0を `chosen_candidate_invariants.json` 等で確認。全5最新シーンのラグ共通性も確認。

### u2/p13のカメラ

図面・建築形状は概算のまま。アイランド角の元観測点に誤りがあり、元の11点と精査後の11点を両方保存。比較は **同じ観測セット同士** で行う。

| 観測セット・原寸RMS px | W | X | 最新Z |
|---|---:|---:|---:|
| u2 元11点 | 21.029 | 17.904 | 19.118 |
| u2 精査11点 | 21.200 | 19.378 | **18.177** |
| p13 元11点 | 16.781 | 14.965 | 16.492 |
| p13 精査11点 | 12.455 | 10.802 | **8.284** |

Wより改善したが **両方とも7px目標は未達**。元条件には未達なら値と理由を記す条項があるが、7pxを達成したという意味ではない。u2最大26.33px、p13最大13.77px。`camera_fit_Z.json` に全値。

- p13観測5/6/7の精査座標は[2125.54,2290.40]、[2110.67,2201.54]、[1944.85,2193.15]。旧7は角から約40px違う。
- u2観測7/8/9/10の精査座標は[4742.84,2222.93]、[5257,2294]、[4717.08,2845.22]、[5218.64,3041.07]。
- u2は主点±2.5%の保守的制約を採用。広い主点可動域の17.114px案はカメラ位置が大きく変わるため不採用。`calibrate_u2_native_conservative_Y.py` が採用元、`calibrate_u2_native_Y.py` はwide比較用で別ファイルに保存。
- p13は `calibrate_native_edges_Y.py` のpinhole案。Brown歪み＋一般Kで6.985pxにできても、実写真の直線に余分な曲がりが出る（直線残差.263→1.861px、最大5.57）ため **不採用**。採用k1=k2=0。歪みを無視したのではなく、検査して追加歪みを却下した。
- Blender実カメラとJSON投影の一致は最大.001462px。これは内部一致であり実空間の精度ではない。
- 独立床線分検証: u2の2軸RMS W3.018/2.421→Z2.417/2.197px、p13 W2.562/.834→Z2.497/.487px。木目線分の可能性もあり実測基準ではない。

## 7. 未解決・注意すべき点

1. **u2最新原寸のレビュー未実施**。Eamesの接地、木部への回り込み、IVRESSE、テーブルとアイランドの継ぎ目、反射・粒状感を最初に拡大確認する。
2. **p01/p13の最新Z原寸未完**。p01は停止前のログだけで合成成功とは言えない。古いパスと混ぜない。
3. **Eamesの旧影ROIは鏡面反射を多く含む**。ROIが暗いことを、そのまま投影影が強すぎる証拠にしない。木部の自然な暗い反射まで薄くしない。
4. 真の影比較として、Eames有／無のShadowCatcher比を固定world環状帯r=.4〜.88m、.04m格子で比較する診断を作成。W/旧Yでは共通1009点、平均比.84025→.85924、影欠損約12%減。ただし **最終Z800Wの結果ではない**。最新Zで再診断予定だった待機ジョブは停止した。
5. 影診断の古い `sun_first_hit` 付帯情報は、shadow不可のphotocardを飛ばさないraycastにより不正確。主環状帯の比とは別。新queueではその付帯情報を空にする。旧値を物理的光路根拠にしない。
6. p01の「家具から離れた、家具の影響のない床」がまだ厳密に特定できていない。固定ROIでは直接・間接遮光でSC約.95、旧RGB差[-1.7,-2.3,-3.3]/255、旧追加閾値.5/255はFAIL。写真の色が近い画素だけ選び直してPASSにしない。新p01はこれから確認する。
7. 窓枠の詳細な落ち影は位置が未確定。写真用シーンは概略の `Glazing_mullion` / `Window_rail` を外した履歴がある。新ラグ上の影について `window_shadow_*Z.py` で候補検査をしたが、**採用変更なし**。Y=0上の一様な窓枠位置は片方の写真に合っても他方で約80px違う。開閉扉・額縁・カーテン等の誤対応の可能性。仮の三角測量XY[5.289237,.150459]も実証されていない。古い枠を一括復活させない。
8. u1右下に巨大に見切れるEamesは、固定カメラと共通配置で近接する結果。Wと同じトリミング08（元画素で[0,1600,4284,4500]）を用意する。見切れだけのためにこの視点の椅子を動かさない。
9. ラグ上の脚には床鏡面反射を無理に出さない。**露出した床上の脚は正しい反射・接地、ラグ上は接触影と圧縮**。既存の床の反射帯はラグの下で遮断する。
10. Toriiのモデルは公式Dining型と未照合。元形状の外形・明るいグレー・Linhaと脚色共有は維持。未認証を「公式」と書かない。
11. 仕上げ・色は写真と視覚参照からの再現。実測反射率、HDR、レンズ校正、建築寸法が揃っているわけではない。数値検査と視覚評価の両方が必要。

## 8. 元の受け入れ条件を維持する

正本は `instructions_X/ACCEPTANCE.md` の **22チェック行**。旧reportの26項目等と混同しない。主要条件:

- 配置5: テーブル短辺0〜数mm、6椅子等の非干渉、レイアウト差分はテーブル＋6椅子、更新平面図で旧420mm注記を消す、見える視点の継ぎ目AOと光漏れなし。最新ラグ追加は追加指示として別記。
- Eames3: 足元の写真既存暗部とW/Zの数値比較、背面の回り込み・最大最小比、W修復済み形状を維持。
- ソファ4: 面平均輝度の標準偏差をWより増やす、窓側暖／陰側冷の数値、p09上面弱い緑、3D材質による縫い目・微細反射。
- カメラ3: u2/p13をWより改善、目標7px／未達理由、脚の接地coverage、他3カメラ差分0。
- 床2: p01のCG追加青み抑制、近傍家具反射維持。
- 共通3: 未加工領域最大誤差2/255以下、grainはW同じで最小.65/255・にじみ同じ、動いた家具で既存窓外景反射遮蔽更新。
- 出力2: 01〜05各JPG/PNG、00一覧、06W比較、07配置図、08同トリミング、packed blend、revision_QA、report、README（参考例・試作CG）。新版はZの名前に対応させる。

FAILを非表示にしたり、ROIや基準を結果に合わせて変えたり、独自の自動確認割合を画質の90%と呼んだりしない。`report_Z.py` は準備済みだが全5視点・shadow検証・SHA紐付きレビューが揃わないと実行完了しない設計。現在まだ実行・納品していない。

## 9. Claudeでの再開手順・今後の予定

### 最初の判断

1. 原文指示、本書、`native_progress.json` を読み、latest設定がSheen .45／sky800／warm200であることを確認。
2. `p09/u1/u2_full_composite.png` を原寸・拡大で見る。特にコーヒーテーブルの光、Eames/IVRESSEの接地、ダイニングの建築との整合、家具の反射、元反射の遮断を確認。
3. 共通シーンを変えるなら、元Xと現在Zを残し新バージョンで全5視点再レンダー。現設定を維持できるなら **p01・p13だけを明示して再開**。u2は出力済みのため先に検証し、不必要なやり直しを避ける。

### 実行環境

現在のWindows作業ルート: `C:\Users\akaay\Documents\Codex\2026-11-03\codex-3d`

Blender: `handoff_dataset/runtime/blender-4.5.9-windows-x64/blender.exe`（4.5.9 LTS）。CPU Ryzen 5700U、RAM約12GB。重いレンダーを複数同時実行しない。

Python: `C:/Users/akaay/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`。主にnumpy、scipy、opencv-python、Pillow、OpenEXR等を利用。別環境では import で依存を確認する。Blender側Pythonは別。

BlenderはPython例外でも終了0のケースがあるため、**`--python-exit-code 1` とログのTraceback検査を維持**。日本語ファイルはUTF-8。

### 残り1視点ごとの処理順（例: p01）

作業ディレクトリーはプロジェクトルート。PowerShell例。`$py` は上記Pythonの実パスを指定する。

```powershell
$blender = (Resolve-Path 'handoff_dataset/runtime/blender-4.5.9-windows-x64/blender.exe').Path
$py = 'C:/Users/akaay/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $blender -b --python-exit-code 1 --python handoff_dataset/prepare_Z.py -- p01
& $blender -b --python-exit-code 1 --python handoff_dataset/render_Z.py -- p01
& $blender -b --python-exit-code 1 --python handoff_dataset/render_Z.py -- p01 --background
& $blender -b --python-exit-code 1 --python handoff_dataset/photo_floor_reflection_Z.py -- p01
& $blender -b --python-exit-code 1 --python handoff_dataset/photo_contact_Z.py -- p01
& $py handoff_dataset/transform_reflection_Z.py p01 full
& $py handoff_dataset/photo_composite_Z.py p01 full
```

各コマンドの成功と出力時刻を確認して次へ。p13も同順。`prepare_Z.py` は **out_Xの各view blendを読み込む依存** がある。最新Zから直接レンダーする案ならprepareを省けるが、改変や欠損を確認すること。進捗JSONは成功した段階だけ更新。`run_native_Z.py` はp09から全5視点をやり直すので再開用ではない。

### 全5視点出た後

1. `verify_rug_Z.py`、`camera_projection_consistency_Z.py`、`photo_inspect_Z.py`、`verify_scene_Z.py` をBlenderで実行。
2. `photo_contacts_check_Z.py`、`metrics_Z.py` を通常Pythonで実行。原寸5枚、変更していない背景画素、grain、露出床の反射、ラグ下遮蔽、カメラ差分を検査。
3. `early_native_colour_Z.py`、`rug_composite_check_Z.py`、`coffee_quality_Z.py` 等の対象範囲を確認して追加評価。`metrics_completed_Z.py` は進捗JSONのcompletedを読むため現在3枚へ更新可能。既存2枚の数値は本書の停止時点を保持。
4. `shadow_separation_Y.py`／`queue_shadow_validation_Z.py` の最終Z用生成部分を確認し、Eames有無の影を切り分ける。旧Wを比較用に使うことと、本番部分パスの再利用は別。
5. p01の床色ROIを物理的影響と照らして評価。u2/p13の建築フィット未達を数値のまま記録する。
6. **全5枚の実画像を原寸で目視**。2枚しか記録のない `visual_review_Z.json` を全5枚の実SHAと実所見で更新する。数字だけで全体品質を合格としない。
7. `photo_details_Z.py`、`photo_master_Z.py`、`report_Z.py`、`assemble_Z.py` を検査して出力。これらは全5枚が揃う前提。report→assemble→report再評価→最新report再配置という段階が必要な場合あり。手順上できたファイルだけを完成扱いしない。
8. 出力一覧とZIPのCRC・展開・パスを検証して渡す。ユーザーはZIPダウンロードエラーを経験し **OneDriveリンク** を希望した履歴がある。新しい最終ZIPを作るなら共有URLも新規に作り、旧Xのリンクを新版と称しない。

### 主要スクリプト索引

| 役割 | ファイル |
|---|---|
| 共通シーン更新・ラグ | `prepare_Z.py`、`add_rug_Z.py` |
| 前景・背景レンダー | `render_Z.py` |
| 5反射パス・AO | `photo_floor_reflection_Z.py`、`photo_contact_Z.py` |
| 反射の色変換 | `transform_reflection_Z.py`、`reflection_display_transform_Z.py` |
| 写真合成・光学・ノイズ | `photo_composite_Z.py`、共通マスクは`photo_common_X.py`→`photo_common_W.py`等 |
| カメラ精査・報告 | `calibrate_u2_native_conservative_Y.py`、`calibrate_native_edges_Y.py`、`camera_fit_report_Z.py` |
| 幾何・不変検証 | `verify_rug_Z.py`、`verify_scene_Z.py`、`camera_projection_consistency_Z.py` |
| 原寸・反射・色・接地 | `metrics_Z.py`、`metrics_completed_Z.py`、`photo_contacts_check_Z.py`、`rug_composite_check_Z.py`、`coffee_quality_Z.py` |
| 影の分離診断 | `shadow_separation_Y.py`、`shadow_isolation_metrics_Y.py`、`queue_shadow_validation_Z.py` |
| 納品編集プロジェクト | `photo_master_Z.py` |
| 比較・報告・納品組立 | `photo_details_Z.py`、`report_Z.py`、`assemble_Z.py`、`plan_Z.py` |
| 選定試行と理由 | `out_Z/WORK_STATUS_Z.md`、`candidate_material_settings.json`、trial系コード／ログ |

`build_pipeline_Z.py` は現在の採用値を生成するが、`build_pipeline_Y.py` をZへ雑にコピーすると古い300W等へ戻るおそれがある。ファイル名にYがあっても最終Zで参照するカメラ・共通処理があるので、Y系を一括削除しない。

## 10. 停止・保管・パッケージについて

停止時に確認した本件プロセスは、`run_native_Z.py`、`validate_after_native_Z.py`、`queue_shadow_validation_Z.py` と、その子のp01前景Blender。停止後に引き継ぎ用master生成だけを別途実行した。レンダー自動継続は再起動していない。

手元の元プロジェクトは削除・上書きしていない。ZIPを作る場合の内容と省略一覧、SHA256は同梱manifestを正とする。ランタイムや膨大な旧試行パスを省略したZIPを、ディスク上の全履歴の完全複製と称しない。元のフル履歴はこのWindows作業場所に残る。

旧共有リンク（履歴としてのみ）:

- W: https://1drv.ms/u/c/59f7d1a8c47bc25c/IQAl4O2CdhqVQqCE5Yy3aLPiAUJh5wbgwF31RHaphYGtBg0
- X: https://1drv.ms/u/c/59f7d1a8c47bc25c/IQBBmIDz4YrkQrfBfKYsGVPlASqdoKDHvBEd7HpqnMR-Fqg

**最新Zの最終納品リンクはまだない。** 引き継ぎZIPは制作途中の資料で、完成納品版ではない。
