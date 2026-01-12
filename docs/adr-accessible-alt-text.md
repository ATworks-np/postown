# ADR: Image の `alt` テキスト必須対応（アクセシビリティ改善）

## 背景 / Context
- Next.js 16（Turbopack）で `next/image` に渡す `alt` が必須となり、空文字や `undefined` の場合にコンソールエラーが発生。
- エラー内容: `Image is missing required "alt" property.`
- 本プロジェクトでは建物画像表示を `BuildingItem` コンポーネントに集約しており、上位から不正な（空の）`alt` が来た場合でも安全に扱いたい。

## 決定 / Decision
- `src/components/BuildingItem.tsx` にて、受け取った `alt` を正規化し、空・未定義であればフォールバック文字列（`"Building image"`）を使用する。
  - 実装: `const safeAlt = (alt ?? '').trim() || 'Building image'`
  - `next/image` の `alt` には `safeAlt` を渡す。
- 呼び出し側（例: `TownStage`）では引き続き可能な限り意味のある `alt`（例: `b.name`）を渡す方針を維持する。

## 影響範囲 / Consequences
- 既存の `BuildingItem` 呼び出しコードは変更不要。
- 空の `alt` が渡ってもユーザー影響（アクセシビリティ低下）を最小化しつつ、最低限の説明テキストが入るため、コンソールエラーが解消される。
- 将来的に `alt` の文言ポリシー（より文脈的・説明的な文）を導入する場合でも、フォールバックは安全網として機能する。

## 代替案 / Alternatives
- 呼び出し元の全てで `alt` の非空を保証する（レビュー/型で縛る）。
  - 型では `string` だが実行時に空文字の可能性は残るため完全ではない。
- ESLint ルールや専用カスタム ESLint で `alt` の妥当性チェックを追加する。
  - 将来的な補完としては有効だが、ランタイムでの安全網は依然必要。

## 実装詳細 / Implementation
- 変更ファイル: `src/components/BuildingItem.tsx`
- 追加ロジック: `safeAlt` を介して `Image` に渡す `alt` を保証。

## 検証 / Verification
- ローカル実行時のコンソールエラー（`Image is missing required "alt" property`）が再現しないことを確認。
- `npm run lint` を実行し、Lint エラーがないことを確認。

## メモ（実装時の気持ち）/ Notes & Feelings
- 画像の代替テキストはアクセシビリティの基本。最低限でもフォールバックを用意しておけば、将来の拡張にも優しくて安心だと感じました。
- これからは `alt` の表現指針（例: 「建物名 + 種別」など）もドキュメント化して、より良い体験を目指したいです。
