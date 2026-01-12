---
title: Xリストの定期取得（毎日）
status: accepted
date: 2026-01-11
---

# 目的

Firestore の `towns` コレクションの各ドキュメントに保存されている `post_group_id`（= X の list_id）を用いて、RapidAPI の `twitter-api45` 経由でリストのタイムラインを毎日取得し、`towns/{townId}/posts` サブコレクションに保存する。

# 背景 / コンテキスト

* プロジェクトでは各タウンに紐づく投稿群を後段の処理で活用したい。
* X(旧Twitter) の公式APIではなく RapidAPI を利用する要件。
* レスポンス構造は `functions/tmp/tweets.json` を参考にする。

# 要件

* スケジュール: 毎日1回の自動実行（Cloud Scheduler / Scheduled Functions）。
* データ取得先: `https://twitter-api45.p.rapidapi.com/listtimeline.php`。
* リクエスト:
  * headers:
    * x-rapidapi-key: 環境変数から取得（`X_RAPIDAPI_KEY` 推奨）。
    * x-rapidapi-host: `twitter-api45.p.rapidapi.com`。
  * params:
    * list_id: Firestore `towns/{id}.post_group_id` を使用。
* 保存先: `towns/{townId}/posts` サブコレクション。
  * ドキュメントID: 自動採番。
  * フィールド:
    * `row_data`: レスポンスのタイムライン1要素（tweetオブジェクト）をそのまま保存。
    * `_created_at`: Firestore サーバータイムスタンプ（`firestore.SERVER_TIMESTAMP`）。
* 既存判定（重複除外）: `row_data.tweet_id` が既に存在する場合は保存しない。

# 設計

* Firebase Functions（Python）で実装。
* スケジュール関数: `fetch_x_lists_daily`（毎日）。
* 手動実行用HTTP関数: `fetch_x_lists_now`（運用テスト・再実行用）。
* Firestore 読み込み: `towns` 全ドキュメントを列挙し、`post_group_id` を `list_id` として RapidAPI に問い合わせ。
* レスポンスの `timeline` 配列をループし、各要素を `row_data` として保存。
* 重複確認は `posts.where('row_data.tweet_id' == tweet_id).limit(1)` による存在チェック。
* バッチ書き込み: 書き込みは 400 件ごとにコミットしてリソース消費を抑制。

# 実装ファイル（モジュール分割後）

* `functions/main.py`
  * Functions エントリポイントのみ（HTTP/scheduled の配線）。
* `functions/src/config.py`
  * Firebase Admin 初期化、Firestore クライアント取得、RapidAPI 設定・キー取得。
* `functions/src/rapidapi_client.py`
  * `fetch_list_timeline(list_id)` RapidAPI 呼び出し。
* `functions/src/timeline.py`
  * レスポンスから `timeline` 配列を抽出するユーティリティ。
* `functions/src/posts_repo.py`
  * `store_posts_for_town(town_id, timeline)` Firestore 保存と重複判定。
* `functions/src/process_towns.py`
  * `process_all_towns()` タウン全件処理のオーケストレーション。

# 環境変数 / 設定

* `X_RAPIDAPI_KEY`（または `RAPIDAPI_KEY`）: RapidAPI のAPIキー
* ローカル開発時は `functions/.env` に設定可能（`python-dotenv` 読み込み）。

# デプロイ / 運用

* 依存関係（抜粋）: `firebase_functions`, `firebase_admin`, `requests`, `python-dotenv`
* `firebase deploy --only functions` でデプロイ。
* スケジュールは `@scheduler_fn.on_schedule("every 24 hours")` で設定済み。
* 手動実行は `https_fn` エンドポイント `fetch_x_lists_now` を叩く。

補足: Node.js/Next 側の JS/TS には変更なしのため、`npm --prefix "$RESOURCE_DIR" run lint` の対象外（Python のみ変更）。

# 代替案の検討

* Node.js 版 Functions での実装も可能だが、現行プロジェクトは Functions(Python) 構成が存在するため Python を採用。
* 取得のページネーション（`cursor`）は今回必須要件に含まれていないため初回は未対応。必要になれば拡張可能な構造とした。

# 影響

* Firestore 書き込み増加。必要に応じて TTL や古いデータのクリーンアップ方針を別途策定。
* `row_data.tweet_id` での検索を行うため、サブコレクション `posts` に対する単一フィールドインデックスで十分。大量クエリが想定される場合にインデックス最適化を検討。

# 実装時の感想・気持ち（ADR所感）

初回は要件に忠実に、重複回避と毎日の自動取得にフォーカスしました。今回、保守性向上のため `functions/src` にモジュール分割し、責務を明確化しました。さらに、各投稿ドキュメントに `_created_at` を付与して後段処理や並び替えをしやすくしました。将来的にページネーション対応やリトライ、レート制限対策、監視（ログ/アラート）を追加したい気持ちです。きちんと動いて、みんなの役に立ちますように。
