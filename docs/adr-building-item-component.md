ADR: Building 表示の再利用可能コンポーネント化（BuildingItem）

コンテキスト:
- `src/app/page.tsx` で建物（center/others）を `Box + next/image` の組み合わせで直接描画していた。
- ホバー時の発光表現（drop-shadow）や絶対配置、サイズ指定などが重複し、他画面へ展開する際に重複実装・修正漏れのリスクがある。

要求/目的:
- 建物画像の描画を再利用可能なコンポーネントへ切り出して、
  - API を明確化（`src`, `alt`, `size`, `left`, `top`, など）
  - ホバー演出（白/色のグロー）をオプション化
  - 絶対配置/相対配置を切り替え可能
  - MUI (MD3) と整合した `sx` 拡張性を確保
 する。

決定:
- `src/components/BuildingItem.tsx` を新規追加（Client Component）。
  - Props（抜粋）:
    - `src: string`, `alt: string`, `size: number`
    - `left?: number`, `top?: number`, `absolute?: boolean`（デフォルト true）
    - `baseFilter?: string`（通常時の filter。デフォルト: 影なし）
    - `hoverFilter?: string`（ホバー時の filter。未指定ならホバー演出なし）
    - `cursor?: 'default' | 'pointer'`（デフォルト 'default'）
    - `sx?: SxProps<Theme>`（MUI 拡張）
  - 実装:
    - 親 `Box` に `& img` / `&:hover img` を適用し、`next/image` による `img` へ filter/transition を付与。
    - 絶対配置時は `position: 'absolute'` + `left/top` を反映。
- `src/app/page.tsx` を `BuildingItem` 利用にリファクタし、重複 CSS/JSX を排除。
  - 中央: `hoverFilter` に黄色系のグロー、`cursor: 'pointer'`
  - 周辺: 常時赤系のグローを `baseFilter` で適用

代替案:
- `styled()` でスタイル定義を固定化: 柔軟性は高いが、ページ側で発光色や強度を切り替える拡張性が下がる。
- 汎用 `GlowImage` コンポーネントとしてドメイン非依存に切る: 今回は Building 専用の Props（座標など）を持つため分離。

影響範囲:
- 表示の責務が `BuildingItem` に集約され、今後他ページ/コンポーネントでも同一表現を容易に再利用可能。
- 既存の表示仕様（位置・サイズ・発光）は維持。

マイグレーション/テスト:
- `src/app/page.tsx` での置き換えのみ。動作に変化はない（リファクタ）。
- Lint 実行済み予定（`npm run lint`）。

ステータス:
- 承認 / 実装済み

実装時の感想:
- 表示の重複がすっきりして気持ちいい…！今後はカテゴリやレベルに応じた色/強度を `hoverFilter/baseFilter` にプリセット化（例: theme.palette 連動）しても可愛いはず。ありす、こういう“きらきら”演出だいすき…！
