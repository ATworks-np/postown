---
title: Town posts サブコレクション一括クリーンアップ（手動実行）
status: accepted
date: 2026-01-11
---

# 目的

特定のタウン `towns/3PJ0B7ZqINXYirzCvVEt` の `posts` サブコレクションから、指定したホワイトリスト以外のドキュメントを一括削除するメンテナンス用バッチを提供する。

# 要件

- 対象タウン: `3PJ0B7ZqINXYirzCvVEt`
- 残すドキュメントID（ホワイトリスト）:
  - `1zbiDopSzk77U7dev5Zv`
  - `VbXqZtbHomOQlokFgBKW`
  - `XpMhDNkxJY8foCCIhZYn`
  - `q9jw6rtW6jFQap8mA51A`
  - `09ebUiHVI72KVCjKWla5`
- その他の `posts` ドキュメントは削除する。
- HTTP エンドポイント（手動実行, now）から呼び出せること。
- 結果としてスキャン数、保持数、削除数、コミット回数を返すこと。

# 設計

- モジュール: `functions/src/batch/cleanup_posts.py`
  - `delete_posts_except(town_id: str, keep_doc_ids: List[str]) -> Dict[str, Any]`
  - 全件ストリームで走査し、ホワイトリストに含まれないドキュメントをバッチ削除。
  - Firestore バッチ上限（500）に余裕を見て 400 件でコミット分割。

- エンドポイント: `functions/main.py`
  - `cleanup_town_posts_now`
  - ハードコードされた対象とホワイトリストで `delete_posts_except` を実行し、結果を JSON で返却。

# 出力例

```json
{
  "town_id": "3PJ0B7ZqINXYirzCvVEt",
  "scanned": 123,
  "kept": 5,
  "deleted": 118,
  "batches_committed": 1
}
```

# 安全性と注意点

- 破壊的操作のため、対象タウンとホワイトリストはソースに固定。
- 実行前に Firestore ルールやバックアップポリシーを確認すること。
- 大量削除時はコストやレート制限に注意。必要に応じてコミットサイズを調整可能。

# 実装時の感想・気持ち（ADR所感）

必要最小限のユースケースに絞り、誤操作を避けるためにハードコード構成にしました。将来的に汎用化する場合は、クエリパラメータやペイロードで town_id / keep_ids を受け取る設計に拡張できるよう、関数インターフェースは汎用のままにしています。安全第一で、しっかりお掃除できますように。
