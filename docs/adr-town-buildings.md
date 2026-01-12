ADR: モデル定義（Town と Buildings サブコレクション）

コンテキスト:
- Firestore をデータストアとして使用する。
- 都市（Town）ドキュメント配下に Buildings のサブコレクションを持つデータモデルが必要。
- 型安全性のため、フロントエンド（Next.js / TypeScript）で interface を定義する。

要求仕様:
- Town ドキュメントは `name` フィールドを持つ。
- Buildings サブコレクションの各ドキュメントは以下のフィールドを持つ。
  - `_created_at`
  - `_deleted_at`
  - `category`
  - `image_url`
  - `level`
  - `name`

決定:
- 以下の TypeScript interface を `src/models/` 配下に作成し、フィールド名を実データに合わせて更新した。
  - `Town`（`src/models/town.ts`）: `name: string`
  - `Building`（`src/models/building.ts`）:
    - `_created_at: string`
    - `_deleted_at?: string | null`
    - `category: string`
    - `image_url: string`
    - `level: number`
    - `name: string`
- 日付はまず `string` として定義。必要に応じて Firestore `Timestamp` 変換ユーティリティを追加予定。

影響範囲:
- 型定義の追加のみで既存機能への影響はなし。

代替案:
- `_created_at` / `_deleted_at` を `Date` や `Timestamp` にする案もあるが、SSG/シリアライズ容易性から `string` を選択。

ステータス:
- 承認 / 実装済み

実装時の感想（ふりかえり）:
- まずは最小限の型から始めて、後でバリデーションや変換を足すスタンスがやっぱり安心。次は Zod 連携や Timestamp 変換ヘルパーを用意したいな。
