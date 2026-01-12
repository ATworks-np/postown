ADR: ルートページに Town 表示（center を中心配置）

コンテキスト:
- ルートページ `/` に特定の Town（ID: `3PJ0B7ZqINXYirzCvVEt`）を表示する。
- Town 配下の Buildings を表示し、`category === "center"` の建物を“ど真ん中”に。それ以外は周囲に配置する。
- App Router、MUI(Material Design 3)、静的ホスティング前提でクライアント取得。

要求仕様:
- Firestore パス: `towns/{townId}` と `towns/{townId}/buildings`。
- フィールド名:
  - Town: `name: string`
  - Building: `_created_at: string`, `_deleted_at?: string | null`, `category: string`, `image_url: string`, `level: number`, `name: string`
- 中心配置の判定:
  - `category === 'center'` の中で、`_created_at` が最も新しい 1 件を中央に配置。
  - 残りの建物は放射状（リング）に均等配置（当面の簡易実装）。
- 画像は Firebase Storage の外部ドメイン URL を next/image で表示。

決定:
- `src/hooks/useTown.ts`, `src/hooks/useBuildings.ts` を新規作成し、読み取り専用でデータ取得。
- `src/app/page.tsx` を実装し、中央建物＋周辺建物を簡易レイアウトで表示。
- `src/app/layout.tsx` で MUI テーマ（`/src/theme/theme.ts`）を適用。
- `next.config.ts` の `images.domains` に `firebasestorage.googleapis.com`, `firebasestorage.app`, `postown-ea4a4.firebasestorage.app` を追加。

代替案:
- 配置アルゴリズムをグリッド／フォースレイアウト／等角投影に進化させる。
- 中心建物の選定を `level` 最大や `最終更新(_updated_at)` に変える。

影響範囲:
- ルーティング直下の UI 実装、Next 画像設定の追加。既存機能への破壊的影響はなし。

ステータス:
- 承認 / 実装済み

実装時の感想:
- まずは“見えること”を重視して放射状の簡易配置に。今後はキャンバスサイズのレスポンシブ最適化と、カテゴリ別リング（例: fun/eco で半径を変える）に挑戦したい。水彩テーマと MUI の相性も良く、絵本っぽい雰囲気が出せて嬉しい！
