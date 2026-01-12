ADR: Building 画像サイズのスケーリングとアスペクト比維持、左下基準のアンカー

コンテキスト:
- Building 表示において「表示幅を `building.size * 20px` にし、高さはアスペクト比を維持する」必要がある。
- 併せて、座標系は左下が (x, y) となる仕様（原点はステージ中心）。
- `next/image` を用いて画像最適化を維持したい。

要求/目的:
- 横幅を `size * 20px` に固定し、縦幅は画像本来のアスペクト比で自動算出。
- 左下基準（画像の左下が (x, y)）を満たすため、CSS 上で `top` は“下端”として扱いたい。

決定:
- `BuildingItem` コンポーネントの API を `size` から `widthPx`（ピクセル値）へ変更。
  - `next/image` には `style={{ width: `${widthPx}px`, height: 'auto' }}` を適用し、アスペクト比を維持。
  - `sizes` 属性に実幅を与える（例: `${widthPx}px`）。
- 左下アンカーのため、コンテナに `transform: translateY(-100%)` を付与。
  - これにより、CSS の `top` が画像の“下端”に対応し、(x, y) の y をそのまま `top = cy - y` で指定可能。
- ページ側（`src/app/page.tsx`）では `widthPx = (b.size ?? 6) * 20` を算出して `BuildingItem` に渡す。

実装:
- 変更: `src/components/BuildingItem.tsx`
  - Props: `widthPx: number` を追加/採用。
  - `next/image` の幅/高さ指定を CSS ベースに切替（`height: 'auto'`）。
  - コンテナに `transform: translateY(-100%)` を付与。
- 変更: `src/app/page.tsx`
  - `widthPx` を算出し、`left = cx + x`, `top = cy - y` で配置。
  - これまでの `top` から高さ分を減算する処理は不要に。

代替案:
- `object-position` を利用してアンカー位置を調整:
  - `next/image` では内部の img へのスタイル適用に工夫が必要で、アンカーの厳密制御が複雑。
- ラッパー要素で下詰めレイアウト（flex/end）:
  - 位置指定（absolute）との併用で複雑化するため見送り。

影響範囲:
- `BuildingItem` の破壊的変更（`size` → `widthPx`）。現状、利用箇所はトップページのみで影響は限定的。
- レイアウト計算式のシンプル化（高さ分減算が不要）。

ステータス:
- 承認 / 実装済み

実装時の感想（ありす）:
- アスペクト比を保ったまま幅基準で揃えると、並べた時の統一感がぐっと増して可愛い…！
- translateY(-100%) で左下アンカーを実現できて、数式も綺麗にまとまって気持ちよかったよ、ますたぁ。
