# ADR: /towns/[id] の静的エクスポート対応（generateStaticParams 導入）

## 背景
Next.js の `output: 'export'`（静的エクスポート）構成で動的セグメント `/towns/[id]` をビルドする際、`generateStaticParams()` が未実装のためビルドエラーとなっていました。

エラー:

```
Page "/towns/[id]" is missing "generateStaticParams()" so it cannot be used with "output: export" config.
```

また、Next.js 16 で `images.domains` が非推奨となり、`images.remotePatterns` へ移行が推奨されています。

## 決定
1. `src/app/towns/[id]/page.tsx` に `generateStaticParams()` を実装し、ビルド時にタウン ID を事前生成する。
   - タウン ID は環境変数 `NEXT_PUBLIC_TOWN_IDS`（例: `tokyo,osaka`）からカンマ区切りで読み取る。
   - これにより、静的エクスポート環境でも `/towns/[id]` が生成可能となる。
2. `next.config.ts` の `images.domains` を削除し、`images.remotePatterns` に移行する。

## 実装詳細
- `src/app/towns/[id]/page.tsx`
  - 以前はクライアントコンポーネントで `useParams` を使用していたが、静的エクスポートの要件に合わせて、サーバーコンポーネントの `params` 経由で ID を受け取り、`generateStaticParams` を定義。
  - 表示自体はクライアントコンポーネント `TownStage` に委譲（既存の挙動維持）。

- `next.config.ts`
  - `images.remotePatterns` に Firebase Storage 等のホストを列挙。

## 代替案の検討
- Firestore 等からビルド時に ID を取得する案もあるが、静的ホスティング前提かつ認証やネットワーク要件、安定性を考慮し、まずは環境変数で制御できる最小構成を採用した。

## 影響範囲
- ビルドパイプラインにおいて `NEXT_PUBLIC_TOWN_IDS` の設定が必要。
- 画像ドメイン設定は非推奨 API からの移行であり、ランタイム動作に悪影響はない。

## 運用
- 新しいタウンを追加したい場合は、ビルド前に `NEXT_PUBLIC_TOWN_IDS` に ID を追加する。

## 実装時の気持ち（ありす）
静的エクスポートでの動的ルートって少しドキドキしちゃうけど、環境変数でスッキリ解決できて良かったのです…！画像設定の警告も消えて、ビルドが気持ちよく通るようになって、ありすもちょっと安心しました。ますたぁが喜んでくれると嬉しいな…！
