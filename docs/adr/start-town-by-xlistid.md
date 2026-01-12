# ルートの「街をはじめる」挙動（xlistid→towns検索→遷移）

## 背景
- ルートページにてユーザーが入力した `xlistid` を基に、Firestore の `towns` コレクションを `post_group_id` で検索し、最初に一致したドキュメントの ID に基づいて `/towns/{doc_id}` へ遷移したい。
- プロジェクト方針として「リアクティブな変数はカスタムフック化」に従い、`useXListId` フックで入力値を管理している。

## 決定
- ルートページ（`src/app/page.tsx`）にて、ボタン押下時に以下を実行する：
  - 入力値をトリミングし空であれば何もしない。
  - Firestore の `towns` を `where('post_group_id', '==', xlistid)` かつ `limit(1)` で検索。
  - 一致があれば最初のドキュメントの `id` を取得して `router.push('/towns/${id}')` で遷移。
  - 一致がなければ `/towns/new` に遷移する（新規作成フローのエントリーページ）。

## 実装詳細
- 依存：`firebase/firestore`, `next/navigation`。
- 変更ファイル：
  - `src/app/page.tsx`
    - Firestore クエリ（`collection`, `query`, `where`, `limit`, `getDocs`）を使用。
    - `useRouter` を利用して動的パスに遷移。

## 影響範囲
- ルートページのボタン挙動のみ変更。既存のステージ描画（`TownStage`）には影響なし。
- `/towns/[id]` ルートが存在していることを前提。未実装の場合は 404 となるため別途実装が必要。
- 新規で `/src/app/towns/new/page.tsx` を追加（プレースホルダー UI）。

## 代替案の検討
- Cloud Functions 経由で ID 解決を行う案：セキュリティや抽象化の面で利点はあるが、現時点ではクエリ 1 回で完結するためクライアント実装を優先。
- 事前に `post_group_id→doc_id` のインデックスマップを保持する案：整合性維持のコストとリアルタイム性の観点から見送り。

## 今後の改善
- `/towns/new` での実際の新規作成フォーム実装（`post_group_id` をクエリで受け取るなど）。
- 一致がない場合のユーザー向けエラーメッセージ表示（Material UI の `Snackbar` など）。
- ローディング状態の可視化（`Button` の `loading`/`disabled` 制御）。
- バリデーション（使用可能文字・長さの制限など）。

## 実装時の感想 / 気持ち
最小変更で要件を満たせて嬉しい気持ち。未一致時に `/towns/new` へ導線を用意できて、次の実装が進めやすくなった。エラー時のユーザー体験は今後もう少し可愛く整えたい…！
