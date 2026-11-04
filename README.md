# 原宿3LDK 試作CG Z3 — 納品ZIP（分割）

参考例・試作CG。納品実績・実測済みの確定プランではありません。

GitHub Releaseを作れない環境のため、100MB未満に分割したZIPをこのブランチに置いています。

```
python3 restore_release.py --extract ./Harajuku_Z3
```

3つの分割ファイルのSHA256、結合後ZIPのSHA256（`release_parts.json`）を検証してから展開します。結合後：`Harajuku_3LDK_delivery_Z3.zip`（345,422,038 bytes、SHA256 ddf0e1a5…6b30384）。Z2版（5視点）はこのブランチの1つ前のコミットにある。

中身：01〜05 原寸PNG/JPG、09_n03・10_n04 追加2視点（00b一覧）、00一覧、06 W→Z2比較、07配置図、08トリミング、source/編集用blend、report.md（原仕様22チェック 22/22：残り3項目はユーザー判断で基準を更新、旧基準と7pxは参考値として記載）、details/検証一式。

制作コードと経緯：ブランチ `codex/harajuku-3d-handoff-z` の `cg/handoff/codex-2026-11-04-Z/`（`CLAUDE_Z2_STATUS.md`）。
