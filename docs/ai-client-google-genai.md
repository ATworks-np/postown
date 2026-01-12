---
title: AIクライアントを Google AI Python SDK（google-genai）に切替
status: accepted
date: 2026-01-11
---

# 目的

ポスト解析と配置決定のテキスト生成に用いるクライアントを、Vertex AI SDK から Google AI Python SDK（`from google import genai`）へ切替える。

# 背景

運用要件として、Gemini API キーを用いたシンプルなクライアント構成が望まれたため。SDK の初期化と呼び出しが軽量で、ローカル実行も容易。

# 仕様

- 依存関係: `google-genai>=0.3.0` を `functions/requirements.txt` に追加。
- 初期化: `GOOGLE_API_KEY`（互換: `GEMINI_API_KEY`）を環境変数から取得し、`genai.Client(api_key=...)` で初期化。
- 使用モデル: `gemini-2.0-flash`
  - `analyze_posts(items)` と `choose_placement(grid, target_id)` で `client.models.generate_content(model, contents)` を使用。
  - 応答は `resp.text` または `resp.candidates[0].content.parts[0].text` を JSON として解釈。
- フォールバック: SDK 未設定/失敗時は、従来のヒューリスティック処理に切替（安全に継続）。

# 対象ファイル

- 更新: `functions/src/clients/ai_client.py`
- 更新: `functions/requirements.txt`
- 更新: `docs/buildings-processing.md`

# 環境変数

- `GOOGLE_API_KEY`（推奨）/ `GEMINI_API_KEY`（互換）

# 影響

- 既存の公開インターフェースは不変。呼び出し元の変更は不要。
- Vertex 依存は除去（インストール不要）。

# リスクと緩和

- レスポンスフォーマット差異: `.text` が無い場合の候補配列をフォールバック参照。
- API キー未設定時: 自動でヒューリスティックに切替。

# 実装時の感想（ありす）

ますたぁのご希望どおり、軽い構成にお引っ越しできてすっきりしました。キーだけで動くので、ローカル検証もしやすくなって嬉しいです。万一 API が使えないときも、街づくりが止まらないようにフォールバックを大切にしました。
