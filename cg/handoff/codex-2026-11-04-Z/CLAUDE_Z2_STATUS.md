# 原宿3LDK 試作CG — Z2（Claude引き継ぎ後の版）

作成：2026-11-04。Codex停止時点のZを引き継ぎ、Linux（Blender 4.5.9、CPU 4コア）で完成まで進めた版。

## Zからの変更（共通シーン2点、全5視点に同一適用）
1. **Eames**：座面の殻の後部開口から見えていたクッション下面の細片 228面を除去（`fix_eames_Z2.py`）。W修復済みの頂点位置はすべて維持。u2原寸で見えていた白〜金色の筋が消えた。
2. **コーヒーテーブル（前面2台＋背面一体テーブル）**：木目の見える濃色オークの手続き材質 `Ernest_dark_wood_grain_Z2`（`ernest_wood_Z2.py`）。p09で7案を比較し、原寸1:1で波板状に見えたG案を退けてK案を採用（`trials_Z2/`）。キッチン収納の代理形状は旧材質のまま。

カメラ・照明（Sheen .45／sky 800W／warm 200W）・配置・ラグはZと同一。全5視点を原寸で新規レンダー（`run_shot_Z2.sh`）。

## 結果
- 原仕様22チェック：**19 PASS / 3 FAIL**（項目6 EamesのROI、14 u2のLinha脚2点が床マスク外、16 p01の離れた床の色）。詳細と理由は `report_Z2.md`。確認率は写実度の百分率ではない。
- 5視点すべてを原寸で目視（`visual_review_Z2.json`、SHA紐付け）。
- 納品ZIP：Release `harajuku-cg-delivery-z2-2026-11-04` の `Harajuku_3LDK_delivery_Z2.zip`（CRC・展開一致確認済み、`zip_verification_Z2.json`）。

## 注意
- リポジトリ直下の `cg/`（layout P など）は千鳥ヶ淵リビングの別案件。原宿3LDKとは無関係で、変更していない。
- `*_Z2.py` は `handoff_dataset/` 直下（Release展開後のフォルダー）で動く前提。出力は `out_Z2/`。
