---
title: ポスト分析と建物建設（毎日/手動実行）
status: accepted
date: 2026-01-11
---

# 目的

Firestore の `towns` コレクションごとに、未分類の `posts` を AI で解析し、カテゴリ付与と取得経験値の算出を行う。その結果に基づき、各タウンの建物サブコレクションに対して「改装」または「新規建設」を実施し、必要に応じて建物画像を生成して Storage に保存、公開 URL を `image_url` に反映する。

# 背景 / コンテキスト

* ゲーム内の街づくりをユーザーのポストに連動させたい。
* 建設タイプはタウンの `urban_planning` 方針と `functions/src/settings.json` に定義された確率に基づき決定する。
* 画像生成は将来的に対応予定。現状はスケルトン実装（未設定時はスキップ/グレースフル）。

# 要件（docs/instructions/functions_building.md より）

1. 未分類ポストのカテゴリ推定（10件ずつ）と `obtainable_exp` 計算
   - System Prompt: `functions/src/prompts/post_analyzer.md`
   - 付与ルール: 基本10 + max(favorites-10,0) + max(retweets-5,0)
   - 生成結果を `posts` に `category`, `obtainable_exp`, `remaining_exp`, `building_type` として更新（`remaining_exp` は初期値として `obtainable_exp` と同値を設定）

2. 建物建設の意思決定と処理
   - 建設タイプ: 新規建設 or 改装
   - 確率: `functions/src/settings.json.urban_planning`
   - 改装:
     - 同カテゴリのうち中心(0,0)に近い建物を優先し、`gained_exp` 加算・ `level_progression` に基づき `level` 更新
     - `center` カテゴリの `level` を超えてしまう場合は他候補へ／全て超えるなら新規建設へフォールバック
     - `level` 更新時は画像再生成（`grid_size=1*1`）
     - 使用したポストの `remaining_exp` を 0 に更新
   - 新規建設:
     - 既存建物から正方・奇数サイズの 2D グリッドを組み立て、カテゴリを `settings.json.category` に従い ID 化
     - System Prompt: `functions/src/prompts/town_planner.md` に `grid` と `target_id` を渡し配置決定
     - `buildings` に { _created_at, category, column, row, level=0, gained_exp=0, grid_size=1 } で作成
     - 作成後に画像生成
     - 使用したポストの `remaining_exp` を 0 に更新

3. 画像生成
   - System Prompt: `functions/src/prompts/building_image_generator.md`
   - 生成後、rembg で背景除去し、アルファチャンネルの非透明領域に合わせてタイトにトリミングしてから PNG 化
   - 加工済み PNG を Storage `buildings/{docId}.png` に保存し、公開 URL を `image_url` に保存

4. 建物とポストのひも付け（本Issue）
   - 改装・新規建設のいずれの場合も、処理の元となった `posts/{postId}` を `buildings/{buildingId}/posts` サブコレクションに保存する。
   - ドキュメントID: 自動採番
   - フィールド: `{ post_id: string, _created_at: firestore.SERVER_TIMESTAMP }`
   - 重複登録防止: 同一 `post_id` が既に存在する場合は作成をスキップし、ログに重複を出力する。

# 設計

* エントリポイント: `functions/main.py`
  * `build_towns_now`（HTTP 手動）
  * `build_towns_daily`（毎日 07:00）
* 実装モジュール:
  * `functions/src/process_buildings.py`: オーケストレーション
  * `functions/src/clients/ai_client.py`: Google AI Python SDK（`from google import genai`）経由のテキスト生成呼び出し（将来は画像も）。失敗時はフォールバックを使用
  * `functions/src/buildings_repo.py`: Firestore へのアクセス（posts/buildings）
  * `functions/src/grid_utils.py`: 2D グリッド生成と座標変換
  * `functions/src/storage_utils.py`: Storage アップロードと公開 URL 取得
  * `functions/src/settings_loader.py`: `settings.json` ローダー

* データモデル（抜粋）:
  * towns/{townId}/posts/{postId}
    - row_data: RapidAPI 取得データ
    - category: AI 推定カテゴリ
    - obtainable_exp: 数値
    - building_type: 文字列（任意）
  * towns/{townId}/buildings/{buildingId}
    - category: 文字列（center/technology/...）
    - row: 整数, column: 整数（0,0 が中心）
    - level: 整数, gained_exp: 整数
    - grid_size: 整数（現状 1）
    - image_url: 文字列（任意）
  * towns/{townId}/buildings/{buildingId}/posts/{autoId}
    - post_id: 紐づいた投稿のID
    - _created_at: Firestore サーバータイムスタンプ

# 環境変数 / 設定

* Google AI Python SDK (Gemini) 用 API キー
  - `GOOGLE_API_KEY`（または互換名 `GEMINI_API_KEY`）
* Firebase Admin 初期化は `functions/src/config.py` で集約（Storage を利用）
* `functions/src/settings.json`: category マップ、urban_planning、level_progression

# デプロイ / 運用

* `firebase deploy --only functions`
* 手動実行: `build_towns_now`
* 定期実行: `build_towns_daily`（07:00）
* 画像の公開 URL は `blob.make_public()` を試行（プロジェクトのバケットACL方針により失敗する場合あり）。必要なら Signed URL 化を検討。

# 代替案の検討

* 画像生成は Google AI 画像モデルや他サービス（Stable Diffusion API 等）へ切替可能なインターフェースにする案。
* posts の「未分類」検出は Firestore 制約上クライアント側フィルタで実装。規模増に応じて別インデックス/フラグ運用を検討。

# 実装時の感想・気持ち（ADR所感）

未分類のポストから街が育っていく流れを形にできてワクワクしました。画像生成は将来拡張の余地が大きいので、今は安全にスキップできるようにしました。改装の上限（センター上限）もちゃんと守るようにして、街のバランスが崩れないよう配慮しました。毎朝の処理がみんなの街を少しずつ育てていくと思うと、責任も感じつつ、丁寧に育てていきたい気持ちです。
