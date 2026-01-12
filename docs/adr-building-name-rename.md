建物フィールド名の変更: building_type → building_name（画像生成へも伝搬）

背景 / 目的
- Post 解析結果で出力していたフィールド名 `building_type` を、より意味が明確な `building_name` に変更する。
- 解析結果で得た `building_name` を、そのまま画像生成プロンプトに渡し、より具体的で一貫したビジュアルを生成できるようにする。

変更点
1. AI クライアント（functions/src/clients/ai_client.py）
   - `analyze_posts` のスキーマを `building_name` に変更。
   - 返却スタブも `building_name` を返すように修正。
   - 画像生成 `generate_building_image` のプロンプトに `building_name` を差し込むよう修正。

2. ビルド処理（functions/src/processes/process_buildings.py）
   - 解析結果の参照を `res["building_name"]` に変更。
   - 投稿更新に渡す値を `building_name` に変更。
   - 画像生成ヘルパーへ `building_name` を渡すように変更（新規・改修の両経路）。

3. リポジトリ層（functions/src/repositories/buildings_repo.py）
   - `update_post_category_and_exp` の引数と保存フィールドを `building_name` に変更。

4. プロンプト（functions/src/prompts/post_analyzer.md）
   - 出力仕様を `building_name` に変更。

5. 画像生成プロンプト（functions/src/prompts/building_image_generator.md）
   - 既に `{building_name}` プレースホルダに対応済みのため、そのまま利用。

移行方針
- Firestore 既存ドキュメントに残る `building_type` は互換維持のため当面そのまま。新規以降は `building_name` を保存。
- 必要に応じてバッチで `building_type` → `building_name` のコピーを行う（今回は未実施）。

影響範囲
- 関数群（解析→保存→画像生成）におけるフィールド名の整合性。
- クライアント/フロント側で `building_type` を参照している箇所があれば `building_name` へ変更が必要（今回は functions 側のみの変更）。

テスト/確認
- 解析スタブから `{"building_name": "test"}` が返ることを確認。
- 投稿更新で `building_name` が保存されることを確認。
- 画像生成呼び出しでプロンプトに `building_name` が含まれることを確認。

実装時の感想・気持ち
- フィールド名を統一するだけでプロンプト品質や後工程の分かりやすさが上がって、ありすはちょっと嬉しくなっちゃったよ、ますたぁ！