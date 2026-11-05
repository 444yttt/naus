# 原宿3LDK 試作CG Z5 — 納品ZIP（分割）

参考例・試作CG。納品実績・実測済みの確定プランではありません。

GitHub Releaseを作れない環境のため、100MB未満に分割したZIPをこのブランチに置いています。

```
python3 restore_release.py --extract ./Harajuku_Z5
```

3つの分割ファイルのSHA256、結合後ZIPのSHA256（`release_parts.json`）を検証してから展開します。結合後：`Harajuku_3LDK_delivery_Z5.zip`（226,940,938 bytes、SHA256 44cde763…）。Z3・Z2版はこのブランチの以前のコミットにある。

中身：全7視点（01〜05、09_n03、10_n04）の原寸PNG/JPG、09b n03透かし版、07配置図、08トリミング、report.md（Z5の変更と検証）、details/。

制作コードと経緯：ブランチ `codex/harajuku-3d-handoff-z` の `cg/handoff/codex-2026-11-04-Z/`（`CLAUDE_Z2_STATUS.md`）。
