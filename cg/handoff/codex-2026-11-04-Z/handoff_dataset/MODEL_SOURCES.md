# MODEL_SOURCES(3Dモデル入手先候補)

確認日: 2026-11-03(JST)、WebSearch による公開ページ確認。**ログイン必須のものは、利用前に必ずユーザー承認を得ること**(エージェントが勝手にアカウント作成・ログインしない)。ライセンスは各モデルページの記載が最優先。

| 入手先 | 内容 | ログイン | ライセンス留意点 | 確認元 |
|---|---|---|---|---|
| **Bang & Olufsen 公式**(Support「Drawings and dimensions」/ Professional Toolbox) | Beolab 28, Beovision Eclipse 等の DWG/OBJ/STP | 不要(公開ダウンロード) | 明示的な利用規約ページは**未確認**。プロ向け設計統合用の公式配布物。再配布は避け、出典を明記 | support.bang-olufsen.com/hc/en-us/articles/360050301211 , bang-olufsen.com/en/int/for-professionals/corporate/professional-toolbox |
| **BoConcept Trade Program** | 2D/3D CAD ライブラリ | **必要**(Trade Program 登録=事業者向け) | 条件**未確認** | boconcept.com/en-us/professionals/trade-program/ |
| **pCon.catalog / pCon.login**(BoConcept) | BoConcept の 3D(例: Fusion アームチェアの 3D ページが公開)。B2B カタログは組織登録+メーカー承認 | 公開閲覧は一部可、ダウンロード/B2B は**必要** | 条件**未確認** | pcon-catalog.com/boconcept/... , login.pcon-solutions.com FAQ |
| **BIMobject**(BoConcept 149製品) | BoConcept のBIM/3D(コーヒーテーブル、アームチェア等) | **必要**(無料アカウント、Google等でも可) | 詳細条件**未確認**(メーカー配布、設計用途想定) | bimobject.com/en/boconcept |
| **B&B Italia** A&D Library | 2D/3D/Revit | **必要**(建築家・デザイナー登録) | **未確認** | content.bebitalia.com |
| **Minotti** | 製品ページに 2d/3d files、BIM(RFA) | ダウンロードエリアは**登録必要**(建築家/正規販売店) | 「著作権保護、インテリアデザイン目的のみ使用許可、その他の使用禁止」と明記 | minotti.com/en/ruffle 等 |
| **Cassina** | 製品ページに 2D/3D(RFA, SKP, 3DS, DWG) | 公式ページでは要否**未確認**(検索結果上はログイン表示なし) | **未確認** | cassina.com/ww/en/products/... , BIMARIUM |
| **Poliform** | 製品ページに 2D DWG / 3D FBX / 3D MAX | 例(Free サイドボード)では直接リンク表示、要否は**未確認** | **未確認** | poliform.it/us/products/free/ |
| **Sketchfab** | 第三者モデル(CC/有料) | ダウンロードは**必要**(アカウント認証) | CC BY は帰属表示必須、NC/ND/SA の制限に注意。ブランド製品の再現モデルは商標・意匠の問題に注意 | sketchfab.com/developers/download-api/guidelines |
| **BlenderKit(現 Blendkit)** | Blender アドオン経由の家具モデル・マテリアル | **必要**(ユーザー登録) | Royalty Free(帰属不要・商用可・モデル単体再販不可)または CC0 | blendkit.com/docs/licenses/ |
| **3dsky.org** | 家具モデル(FREE / OM=メーカー公式 / PRO=有料) | **必要**。FREE/OMは 1日3点まで、PRO は有料 | 非独占・個人的・譲渡不可・取消可能なライセンス | 3dsky.org/faq/165, /189, /115 |
| CGTrader 等(参考) | 例: Beolab 28 有料モデル(Custom License) | 必要・有料 | 購入=要ユーザー承認 | cgtrader.com |

## 同梱済みモデル(models/)
| ファイル | 製品 | 形式・単位 | 出典 |
|---|---|---|---|
| models/original_zip/eclipse65_floor.zip, models/eclipse65/STAND/BV_ECLIPSE_65_ON_STAND.{obj,dwg,stp} | Beovision Eclipse 65 on floor stand | OBJ, mm, Y-up(ファイル日付 2017-08) | B&O 公式 3D Drawings(前回作業で取得。正確なダウンロードURLは記録が残っておらず**未確認**、上記 B&O Support ページ経由) |
| models/original_zip/beolab28.zip, models/beolab28_obj/*.obj | Beolab 28(woofer_floor / woofer_wall / tube_basic / fabric_curtain_off / wooden_curtain_off) | OBJ, mm, Y-up(2021-03) | B&O 公式 Beolab 28 ページ「3D Drawings」 |
利用は本試作CGの制作用途に限り、データセットの外部再配布は避けること。MTL/テクスチャは含まれない(マテリアルは自前設定)。
