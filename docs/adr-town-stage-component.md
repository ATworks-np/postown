ADR: 街表示の再利用可能コンポーネント化（TownStage）

コンテキスト:
- これまでルートページ（`src/app/page.tsx`）で街（Town/Buildings）の取得・ステージサイズ計算・描画（`BuildingItem` 群）・オーバーレイ UI を一体で実装していた。
- 他ページでも同じ街表示を再利用したい、という要望が出てきた。
- 本プロジェクトは Next.js(App Router) + Material UI(Material Design 3) で構築しており、Client コンポーネントでの動的描画が前提。

要求/目的:
- 「街のステージ」を独立した再利用コンポーネントとして切り出す。
  - データ取得（`useTown`, `useBuildings`）
  - ステージサイズの動的追従（`useWindowSize`）
  - 座標系（原点＝ステージ中央、左下アンカー）に基づく描画
  - MD3/MUI でのスタイル
- オーバーレイ UI（テキスト入力やボタンなど）を、呼び出し側が `children` で自由に重ねられる API にする。

決定:
- `src/components/TownStage.tsx` を新規作成（Client Component）。
  - Props:
    - `townId: string`（必須）
    - `unitPx?: number`（デフォルト 30）: Building の `size` から算出する 1 単位のピクセル幅
    - `minWidth?: number`（デフォルト 320）, `minHeight?: number`（デフォルト 240）
    - `containerVerticalPadding?: number`（デフォルト 64）: ルート Container の上下パディング分
    - `containerSx?: SxProps<Theme>`: 外側 Box への追加 `sx`
    - `children?: React.ReactNode`: ステージ上に重ねる任意の UI
  - 内部実装:
    - `useTown(townId)`, `useBuildings(townId)`, `useWindowSize`
    - ステージの幅/高さを window サイズから算出し、原点を中央に設定（`cx`, `cy`）
    - `BuildingItem` を使って、(x, y) を左下アンカーで `left/top` に変換して描画
    - `category === 'center'` にはホバー黄色グロー、その他は赤のベースグロー
- ルートページ（`src/app/page.tsx`）は `TownStage` を利用し、オーバーレイの入力 UI を `children` で提供する形にリファクタした。

代替案:
- Context や Provider で共有し、ステージは薄いラッパーに留める: 柔軟だが、今回の要件ではコンポーネント単体で完結させた方が再利用が簡単。
- Canvas/WebGL での描画: 表現力は高いが、既存の `next/image` や MUI テーマとの整合が難しく、今回は見送り。

影響範囲:
- ルートページの記述量が大幅に減り、オーバーレイ UI のみを記述すれば良くなった。
- 既存の座標系・サイズスケーリング・発光演出は維持される。

マイグレーション/テスト:
- `src/app/page.tsx` を `TownStage` を使う形に置き換え。
- `npm run lint` で静的検査を通過することを確認。

ステータス:
- 承認 / 実装済み

実装時の感想（ありす）:
- ロジックをきれいにひとつの箱（コンポーネント）にまとめるの、すっごく好き…！呼び出し側が `children` で好きに UI を重ねられるのも、使い勝手がよくてワクワクしちゃう。ますたぁ、次はどのページにこの街を飾る？