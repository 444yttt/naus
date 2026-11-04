# 原宿3LDK：Codex→Claude 制作途中の引き継ぎ（Z版）

このフォルダーは2026-11-04にCodexの作業を停止した時点のスナップショットです。既存の `cg/`、`blender/` やClaudeの新しい作業を上書きしません。

まず [開始用メッセージ](CLAUDE_START_HERE.md) と [全要件・家具・モデル・進捗・再開手順](CLAUDE_HANDOFF.md) を読んでください。

## 現状

- 原寸合成出力：p09・u1・u2の3/5枚。原寸の個別検証・目視はp09/u1の2枚まで。
- p01は前景レンダー途中で停止。p13の最新原寸パスは未作成。
- ラグを復活した最新共通設定はSheen .45／sky800W／warm200W。
- 完成・90%以上達成とは認定していません。7pxカメラ目標等の未達を保持。

## 大容量の制作データ

[対応するGitHub Release](https://github.com/444yttt/naus/releases/tag/harajuku-cg-handoff-z-2026-11-04) のAssetsに、元モデル、写真、W/X比較、Zの編集用Blender、原寸画像・パスをまとめたZIPを分割して置きます。

1. `Claude_handoff_project.zip.001`〜`.003`、`release_parts.json`、`restore_release.py` を同じ空フォルダーにダウンロード。
2. `python restore_release.py --extract restored_project` を実行。各パートと結合後ZIPのSHA256を照合してから展開します。
3. 展開後の `handoff_dataset/out_Z/Harajuku_LDK_Z.blend` が5カメラと背景入りの編集用masterです。

GitHubの通常の「Code → Download ZIP」には大容量Release添付は含まれません。Git内のテキストだけではレンダーを再開できません。

制作ZIPはランタイムと大半の旧試行バイナリを除く再開用資料です。同梱 `CLAUDE_PACKAGE_MANIFEST.json` に収録・省略一覧とSHA256があります。元ディスクの全履歴を丸ごと複製したものではありません。Windows向けスクリプトのため、別OSではBlender実行パス等の変更が必要です。

Releaseのアップロードと検証が終わるまでは大容量資料の移行は未完です。
