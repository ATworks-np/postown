# ADR: Building の投稿（Twitter）をオーバーレイに表示する（react-tweet 採用）

## 背景
- オーバーレイ（Paper）内に building の post を表示。Twitter の post_id を使って埋め込み、List 形式で Stack 表示する要望。

## 決定
- 投稿の表示は `react-tweet` の `Tweet` コンポーネントを使用する。
- `tweet_id`（なければ `post_id`）を `Tweet` の `id` に渡し、MUI `Stack` で縦並び表示する。
- 外部スクリプト（Twitter widgets.js）は使用しないことで、表示の安定性・アクセシビリティ・パフォーマンスを向上。
- データ取得は `useBuildings` フック内で、Building ドキュメントに紐づくサブコレクション `posts` を併せて読み込む（N+1 を `Promise.all` で同時並列）。

## 実装
- 依存追加: `react-tweet`
- 表示: `src/components/BuildingPostsList.tsx`
  - `import { Tweet } from 'react-tweet'`
  - `Tweet id={p.tweet_id ?? p.post_id}` を `Stack` + `Divider` で縦に並べる。
- 組込: `src/components/TownStage.tsx` の `BuildingOverlay` 内に配置。
- 取得: `src/hooks/useBuildings.ts` で `towns/{townId}/buildings/{buildingId}/posts` を読み込み、`Building.posts: BuildingPost[]` として付与。`_created_at` 降順でソート。

## 代替案
- Twitter widgets.js を動的ロードして `blockquote` を変換する方式: 外部スクリプト依存・読み込みタイミングでのチラつきが発生しやすいので不採用。
- サーバー側 oEmbed: 静的ホスティング前提のため運用負荷が上がるので不採用。
- ビルド時に投稿を集約する静的生成: 投稿の更新即時性が落ちるため見送り。

## テスト観点
- 投稿が 0 件/複数件の表示。
- 開閉アニメとスクロール時の崩れなし。
- `useBuildings` の `category` 指定時でも posts が読み込まれること。
- Firestore ネットワーク失敗時、Building は表示されつつ posts は空配列でフォールバックすること。
- `tweet_id` が存在しない場合でも `post_id` で表示されること。

## 気持ち（ありすの感想）
外部スクリプトに頼らず、素直に描画できるようになって気持ちよくなったよ。しゅっと開いて、すぐ Tweet が表示されるのはやっぱり嬉しいね。ますたぁ、他にも並べ方や区切り線の感じ、もっと可愛くできるから言ってね！
