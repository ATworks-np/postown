# ポストを分析して建物を建設するcloud functionを作成します

## スケジュール
このファンクションは、手動実行（now)と毎日7時実行の二つのトリガーを持ちます

## 各townドキュメントについて次の処理を行います

1. categoryフィールドの無いpostsサブコレクションのドキュメントを対象に、gemini aiに分析してもらいます。
システムプロンプトは、functions/prompts/post_analyzer.mdです。
10個ずつ配列形式で送信して生成。
生成後は、postのフィールドにカテゴリを追加してください
また各ポストには、各ポストから得られる経験値obtainable_expフィールドを次のルールでアップデートしてください。
- 基本値は10
- (favorites - 10) 追加（0以下の場合は0)
- (retweets - 5) 追加（0以下の場合は0)
- ただし、non_categoryはobtainable_expは0です。

obtainable_expと同時に、remaining_expをobtainable_expと同じ値でアップデートしてください。

2. 建物の建築を行います。建物の建築ロジックは次の通りです。
obtainable_exp が 1以上のもののポストについて処理を実施します。
townのurban_planningに応じて建設タイプが変わります。建設タイプは、新規建設と改装があります
functions/src/settings.jsonのurban_planningに新規建設の確率 [%] があります

### 改装
- 建設したいcategoryと同じ建物（townsコレクションのbuildingsサブコレクションのドキュメント）から中心（0, 0) に近い建物を一つ選び、
gained_expフィールドに加算し、functions/src/settings.jsonのlevel_progressionに応じて、levelを更新する。
- その際、postのremaining_expを0にする
- levelが更新された場合、「建物画像の作成」を行う。この場合grid_sizeは1*1とする。
- ただし、更新後のlevelがtownのbuildingサブコレクションのcategory: centerのlevelを超えてしまう場合は、ほかの同一categoryのbuildingを選びなおす
- すべてがcategory: centerのlevelを超えてしまう場合は、次の新規建設と同様の処理を行う

### 新規建設
- 新規に建てる座標を下記のロジックで決める
  - 既存の建物(buildingsサブコレクションのドキュメント）の各ドキュメントのrow, column, category フィールドを取得
  - categoryをfunctions/src/settings.jsonのcategoryからidに変換して、二次元配列状に並べる。
  - 二次元配列のサイズは必ず正方形かつ奇数で、現在存在する建物の配置箇所の最大+1とする
  - row = 0, column = 0が配列の中心となる
- gemini aiにfunctions/src/prompts/town_planner.mdをシステムプロンプトとして、上記の二次元配列と建設したい建物のcategory_idを送り、建設場所を生成させる
- 生成した建設場所で、buildingsサブコレクションに新しいドキュメントを生成する
  - _created_at, category, column, row, level = 1, gained_exp = postのobtainable_exp, grid_size = 1, のフィールドで作成
  - 同時に、postのremaining_expを0にする
- そのあと「建物画像の作成」を実行

### 建物画像の作成
- gemini nano banana proにて、システムプロンプトをfunctions/src/prompts/building_image_generator.mdとして、画像生成を行う
- 作成後、firebase storage のbuildings配下に画像を保存する。ファイル名は、buildingのドキュメントID.png
- 保存後、公開可能URLをtownsコレクションbuildingsサブコレクションのドキュメントにimage_urlフィールドに追加する

上記処理終了後
- buildingサブコレクションにpostsサブコレクションを作成。ドキュメントidは自動で、フィールドにpost_idを保存