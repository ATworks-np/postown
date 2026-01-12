---
title: AIクライアントのVertex AI（google-cloud-aiplatform）移行
status: accepted
date: 2026-01-11
---

# 目的

既存の Gemini SDK（google.generativeai）依存を廃し、Google Cloud の Vertex AI（google-cloud-aiplatform）経由で Gemini モデルを呼び出す構成へ移行する。これにより、GCP 権限管理・監査・将来的なモデル切替を GCP 側に集約し、運用性を高める。

# 背景

これまで `functions/src/clients/ai_client.py` は `google.generativeai` を直接利用していたが、Cloud Functions(Python) での運用においては GCP のサービスアカウント認証やリージョン設定を Vertex AI に統一する方が管理が容易である。

# 対象

- `functions/src/clients/ai_client.py`
- ドキュメント: `docs/buildings-processing.md`（環境変数の記載更新）
- 依存: `functions/requirements.txt` に Vertex AI SDK を追加

# 仕様

- 初期化
  - 環境変数 `GOOGLE_CLOUD_PROJECT`（または `GCLOUD_PROJECT`/`PROJECT_ID`）と `VERTEX_LOCATION`（または `GOOGLE_CLOUD_REGION`。既定は `us-central1`）を用いて `vertexai.init(project, location)` を実行。
  - 初期化に失敗した場合や環境変数が無い場合は、従来通りのヒューリスティック・フォールバックで安全に動作継続。

- 使用モデル
  - `GenerativeModel("gemini-1.5-flash")` を利用。
  - `analyze_posts` と `choose_placement` は、プロンプト（MD）+ JSON で入力を与え、返却テキストを JSON として解析。

- 画像生成
  - 将来的に Vertex AI 画像モデルを統合するが、現時点ではプレースホルダ（未実装）とする。

# 例外・フォールバック

- Vertex AI SDK または環境が利用できない場合は、
  - `analyze_posts`: キーワードに基づく簡易分類ヒューリスティックを使用
  - `choose_placement`: 中心に最も近い空き地（0）を選ぶ簡易配置

# 環境変数

- `GOOGLE_CLOUD_PROJECT`（推奨）/ `GCLOUD_PROJECT` / `PROJECT_ID`
- `VERTEX_LOCATION`（任意。無い場合は `us-central1`）/ `GOOGLE_CLOUD_REGION`

# セキュリティ

- 認証はデフォルトのアプリケーション認証情報（サービスアカウント）を使用。追加のAPIキーは不要。

# 依存関係

依存追加: google-cloud-aiplatform (Vertex AI SDK)

# 移行影響

- 外部インターフェース（`AIClient` の公開メソッド）は変更なし。
- 実行環境に GCP プロジェクトと Vertex AI API の有効化が必要。

# 実装時の感想・気持ち（ADR所感）

ありす、ますたぁの街づくりを支えるAIまわりを Vertex に合わせてお引っ越ししました。GCP に揃うことで運用がすっきりして、将来の拡張もやりやすくなって嬉しいです。画像生成は次の楽しみとして取っておきますね。みんなの街がもっと素敵になりますように。
