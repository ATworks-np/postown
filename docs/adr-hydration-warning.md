ADR: Hydration 警告（属性不一致）の対処

コンテキスト:
- Next.js(App Router) + MUI で SSR を行う際、クライアント側ハイドレーション時に
  「A tree hydrated but some attributes of the server rendered HTML didn't match the client properties.」
  という警告がブラウザコンソールに表示されることがあった。
- MUI のクラス名/スタイル注入タイミング（Emotion）や `next/font` による `className` 付与などで、
  SSR と CSR の属性が一時的に不一致になることがある。

要求/目的:
- 警告の解消（少なくとも無害な差分は抑止）し、ユーザー体験とデベロッパー体験を改善する。

決定:
- `src/app/layout.tsx` の `<html>` に `suppressHydrationWarning` を付与し、
  SSR/CSR 間で一時的に発生し得る無害な属性差分を無視させる。
- さらに、ブラウザ拡張（例: ショートカット/ジェスチャ系拡張）が `body` に独自属性（例: `cz-shortcut-listen="true"`）を注入して
  しまうケースに対応するため、`<body>` にも `suppressHydrationWarning` を付与した。
- テーマ提供は Client Component の `ThemeRegistry`（`AppRouterCacheProvider` + `ThemeProvider`）で行い、
  Server → Client 間で関数を直接渡さない構成を維持する。

変更点:
- 更新: `src/app/layout.tsx`
  - `<html lang="ja" suppressHydrationWarning>` に変更。
  - `<body suppressHydrationWarning className="...">` に変更。

代替案:
- MUI の SSR 設定をさらに厳密化（Emotion のサーバーサイドキャッシュを自前実装）:
  - 効果はあるが App Router 向けの推奨は `@mui/material-nextjs` の `AppRouterCacheProvider` 採用で十分なため今回は見送り。
- `suppressHydrationWarning` を `<body>` に付ける:
  - `html` に付ける方が広く安全で確実。

影響範囲:
- 表示のロジックには影響しない。SSR/CSR 間の一時的不一致に関する警告が抑止される。

ステータス:
- 承認 / 実装済み

実装時の感想（ありす）:
- こういう“チラッ”と出る警告、気になってソワソワしちゃうよね…！
- 今回は拡張機能が `body` に属性を差し込んでて、予想外のところでミスマッチが起きてたの。
  `html` だけじゃ抑えきれないケースもあるから `body` にも付けて、しっかり静かにしてもらったよ。
  ますたぁの開発体験、大事にしたいの…！
