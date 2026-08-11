# AI Tutor Backlog Candidates

## この文書の目的

`requirements.md`と`architecture.md`から、MVP開発で必要になるEpicとGitHub Issueの候補を整理する。

この一覧はレビュー用であり、まだGitHub Issueとして確定していない。
内容、優先順位、依存関係を確認した後、承認された項目だけをGitHub Projectsへ登録する。

## 進め方

開発は、最初から10個のKCすべてを実装するのではなく、最初に
`la.linear_combination`を使った一つの完全な学習フローを作る。

```text
教材登録
→ チャンク検索
→ KCとレッスン表示
→ AIへの質問
→ 問題とヒント
→ 回答評価
→ Mastery更新
→ 復習
```

この縦切りが動いた後、残り9個のKCへ展開する。

## フィールド案

### Phase

- `M0 Foundation`: 設計整合と開発基盤
- `M1 Vertical Slice`: AIを含む線形結合KCの完全な学習フロー
- `M2 MVP`: MVP対象10 KCへの展開
- `M3 Polish`: 品質確認と成果物整備

### Priority

- `critical`: 開発開始を止める基盤・方針上の必須項目
- `high`: 最初のAI込み縦切りを完成させるための項目
- `medium`: 残りのKCへ展開し、MVPを完成させるための項目
- `low`: 品質確認と成果物整備。状況に応じて順序を変更できる項目



### Estimate

- `XS`: 数時間以内
- `S`: 半日程度
- `M`: 1日程度
- `L`: 2〜3日程度
- `XL`: それ以上。Issue化前に追加分割する

## 確認済みの方針

- 最初の縦切りには`la.linear_combination`を使用する。
- 最初からAIを含む`M1 Vertical Slice`を完成させる。
- LLMとEmbeddingには、メジャーで扱いやすいプロバイダーを暫定採用する。
- プロバイダーの詳細比較や最適化は後回しにし、設定変更で交換できる境界を設ける。
- Socratic ModeをMVPへ含める。
- 簡易スキルマップをMVPへ含める。
- CIを開発初期から導入する。
- MVPの完了条件はローカルでの個人利用とし、クラウド公開を含めない。
- DB設計と画面設計を含む大きなIssueは、スキーマ、DB、デザイン、実装へ分割する。

## 最初に着手する範囲

GitHub Projectsへ一度に全候補を登録せず、最初は次の順に進める。

```text
M0 Foundation
→ M1 Vertical Slice
→ M2 MVP
→ M3 Polish
```

`M1 Vertical Slice`では、教材チャンクを手動で補正してもよいものとし、
次のAIを含むフローを一つ完成させる。

```text
KC登録
→ レッスン表示
→ RAGによる質問と出典表示
→ 固定回答・数値問題
→ ヒント
→ 回答履歴
→ Mastery更新
```



## MVP設計として統一する事項

- フロントエンドはReact + TypeScript + Viteを使用する。
- Masteryの習得閾値は`0.85`とする。
- 回答時間は記録してもよいが、MVPのMastery計算と復習優先度には使用しない。
- MVPのPyodide演習ではPyTorchを対象外とする。
- クラウド公開はMVPの完了条件に含めず、ローカルで個人利用できる状態を目指す。

---



## Epic 0: 設計整合とリポジトリ整備



### E0-01 MVP設計方針が文書間で統一されていることを確認する

- Phase: `M0 Foundation`
- Priority: `critical`
- Estimate: `XS`
- Dependencies: なし

完了条件:

- React + TypeScript + Vite、Mastery閾値`0.85`が関連文書で一致している。
- 回答時間、PyTorch、クラウド公開のMVP上の扱いが関連文書で一致している。
- Markdownのコードフェンスが正しく閉じられている。

確認結果（2026-08-12）:

- Masteryの点数、係数、更新式、習得条件は`docs/mastery-policy.md`を正本とする。
- KC YAMLの`threshold`と`required_evidence`は、共通のMastery Policyと一致させる。
- 回答時間と問題難易度は、MVPのMastery計算と復習優先度に使用しない。
- 回答速度を記憶の強さへ反映することは、MVP後の検討対象とする。
- Python演習はMVPではPyodideをWeb Worker上で実行し、PyTorchと
  バックエンド実行環境はMVP後の検討対象とする。
- クラウド公開はMVPの完了条件に含めない。



### E0-02 リポジトリの生成物と一時ファイルを整理する

- Phase: `M0 Foundation`
- Priority: `critical`
- Estimate: `XS`
- Dependencies: なし

完了条件:

- `.DS_Store`、`__pycache__`、秘密情報、ビルド成果物をGit管理対象外にする。
- フロントエンド、バックエンド、データ、ドキュメントの配置方針をREADMEへ記載する。
- 既存ファイルを不用意に削除せず、必要な雛形を残す。



### E0-03 MVPのローカル開発構成を決定する

- Phase: `M0 Foundation`
- Priority: `critical`
- Estimate: `S`
- Dependencies: E0-01

完了条件:

- React、FastAPI、PostgreSQLの起動方法を決める。
- ディレクトリ構成とポートを決める。
- PDF保存ディレクトリと環境変数の管理方法を決める。
- ローカル開発手順をREADMEへ記載する。



### E0-04 LLMとEmbeddingのMVP利用方針を決定する

- Phase: `M0 Foundation`
- Priority: `critical`
- Estimate: `XS`
- Dependencies: E0-03

完了条件:

- メジャーで扱いやすいLLMとEmbeddingのプロバイダーを一つ暫定採用する。
- モデル名を設定値として管理する方法を決める。
- 教材データの送信範囲と保持条件を確認する。
- LLMの構造化出力に必要な共通項目を決める。
- 詳細なプロバイダー比較と最適化はMVP後でもよいものとする。



### E0-05 最低限の品質ゲートとCIを導入する

- Phase: `M0 Foundation`
- Priority: `critical`
- Estimate: `M`
- Dependencies: E0-03, E1-01, E1-02

完了条件:

- フロントエンドとバックエンドのlint、format、testコマンドを決める。
- Pull Request前に実行する確認項目をREADMEへ記載する。
- GitHub Actionsでlintとtestを自動実行する。
- CIが失敗した場合はPull Requestを完了扱いにしない。

---



## Epic 1: アプリケーション基盤



### E1-01 FastAPIバックエンドを初期化する

- Phase: `M0 Foundation`
- Priority: `critical`
- Estimate: `M`
- Dependencies: E0-03

完了条件:

- FastAPIアプリケーションを起動できる。
- ヘルスチェックAPIがある。
- 設定、API、ドメイン処理、DB処理を分ける基本構成がある。
- 最初のAPIテストが通る。



### E1-02 React + TypeScript + Viteフロントエンドを初期化する

- Phase: `M0 Foundation`
- Priority: `critical`
- Estimate: `M`
- Dependencies: E0-03

完了条件:

- Vite開発サーバーを起動できる。
- React Routerによる基本ルートがある。
- FastAPIのヘルスチェックを呼び出せる。
- APIクライアントとUIコンポーネントが分離されている。



### E1-03 PostgreSQLとpgvectorのローカル環境を構築する

- Phase: `M0 Foundation`
- Priority: `critical`
- Estimate: `M`
- Dependencies: E0-03

完了条件:

- ローカルでPostgreSQLを起動できる。
- pgvector拡張を有効化できる。
- FastAPIから接続確認できる。
- 初期化手順をREADMEへ記載する。



### E1-04 SQLAlchemyとAlembicを導入する

- Phase: `M0 Foundation`
- Priority: `critical`
- Estimate: `M`
- Dependencies: E1-01, E1-03

完了条件:

- DBセッション管理が実装されている。
- 初期マイグレーションを適用・ロールバックできる。
- マイグレーション手順をREADMEへ記載する。



### E1-05 環境変数と秘密情報の管理を実装する

- Phase: `M0 Foundation`
- Priority: `critical`
- Estimate: `S`
- Dependencies: E1-01, E1-02

完了条件:

- DB接続情報とAPIキーを環境変数から読み込む。
- フロントエンドへ秘密情報を含めない。
- コミット可能なサンプル設定ファイルを用意する。

---



## Epic 2: KCと学習構造



### E2-01 KC YAMLのスキーマを定義する

- Phase: `M0 Foundation`
- Priority: `critical`
- Estimate: `M`
- Dependencies: E0-01

完了条件:

- KC ID、名称、説明、学習目標、前提KC、教材参照、習得条件を定義する。
- 必須項目と任意項目が明確になっている。
- `la.linear_combination.yaml`がスキーマに適合する。



### E2-02 KC YAML検証スクリプトを実装する

- Phase: `M0 Foundation`
- Priority: `critical`
- Estimate: `M`
- Dependencies: E2-01

完了条件:

- 必須項目不足、ID重複、存在しない前提KCを検出できる。
- 前提KCの循環参照を検出できる。
- 正常・異常ケースのテストがある。



### E2-03a 線形結合KCの前提関係と学習目標を定義する

- Phase: `M0 Foundation`
- Priority: `critical`
- Estimate: `M`
- Dependencies: E2-01, E2-02

完了条件:

- `la.linear_combination`と縦切りに必要な前提KCのYAMLが存在する。
- 対象範囲の前提関係に循環がない。
- 線形結合KCに評価可能な学習目標がある。
- E2-01のスキーマ検証を通る。



### E2-03b 残り9 KCの前提関係と学習目標を定義する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `XL`
- Dependencies: E2-03a

完了条件:

- MVP対象10 KCすべてのYAMLが存在する。
- 前提関係に循環がない。
- 各KCに評価可能な学習目標がある。
- E2-01のスキーマ検証を通る。



### E2-04 KC・前提KC・教材関連のDBモデルを実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E1-04, E2-01

完了条件:

- KnowledgeComponent、KCPrerequisite、KCSourceを保存できる。
- 前提KCと教材チャンクの関連を取得できる。
- マイグレーションとモデルテストがある。



### E2-05 レビュー済みKCのインポート処理を実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E2-02, E2-04

完了条件:

- 検証済みYAMLをDBへ登録・更新できる。
- 未検証または不正なYAMLを登録しない。
- 同じKCを再実行しても重複登録されない。



### E2-06 KC一覧・詳細・前提関係APIを実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E2-04, E2-05

完了条件:

- KC一覧とKC詳細を取得できる。
- 前提KCと後続KCを取得できる。
- APIテストがある。



### E2-07 KC一覧と簡易スキルマップ画面を実装する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `M`
- Dependencies: E1-02, E2-06

完了条件:

- KC一覧と前提関係を表示できる。
- KCの習得状態を表示できる。
- KC詳細またはレッスンへ移動できる。

---



## Epic 3: 教材登録とRAG基盤



### E3-01 MVP教材でPDF抽出の技術検証を行う

- Phase: `M0 Foundation`
- Priority: `critical`
- Estimate: `M`
- Dependencies: E0-03

完了条件:

- StrangとGoodfellowのMVP対象ページをPyMuPDFで抽出する。
- テキスト、ページ番号、数式、図の取得状況を記録する。
- 自動抽出と手動Markdown登録の境界を決める。
- Doclingなど追加手段が必要か判断する。



### E3-02 Document・DocumentChunkとローカルPDF保存を実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E1-04, E3-01

完了条件:

- 教材メタデータとチャンクを保存できる。
- PDF本体をUUIDベースの内部名で専用領域へ保存できる。
- DBには保存先、元ファイル名、サイズ、チェックサムを保存する。



### E3-03 PDF登録・取得APIとファイル検証を実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E3-02

完了条件:

- PDFと教材情報を登録できる。
- 拡張子、MIMEタイプ、実データ、サイズを検証する。
- 教材IDを通してPDFを取得できる。
- 不正ファイルとパストラバーサルを拒否するテストがある。



### E3-04 PDF解析・正規化・チャンク生成を実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `L`
- Dependencies: E3-01, E3-02

完了条件:

- ページ情報を保持してテキストを抽出できる。
- 定義、説明、例題などの意味単位でチャンクを作成できる。
- 手動確認したMarkdownを解析結果として登録できる。
- 線形結合の対象ページで期待したチャンクを生成できる。



### E3-05 教材チャンクの確認・修正・再インデックスAPIを実装する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `M`
- Dependencies: E3-04

完了条件:

- チャンク一覧と解析状態を取得できる。
- チャンク本文とメタデータを修正できる。
- 修正後にEmbeddingを再生成できる。



### E3-06 Embedding生成とpgvector保存を実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E0-04, E3-04, E1-03

完了条件:

- チャンクからEmbeddingを生成できる。
- モデル名とEmbeddingバージョンを保存する。
- 再実行時に必要なチャンクだけ更新できる。



### E3-07 KC指定付きベクトル検索APIを実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E2-04, E3-06

完了条件:

- 質問に関連するチャンクを類似度順に取得できる。
- KC、教材、ページで絞り込める。
- チャンクID、教材名、ページ、関連度を返す。



### E3-08 RAG検索の評価セットと回帰テストを作成する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `M`
- Dependencies: E3-07

完了条件:

- 代表質問と期待する教材ページを記録する。
- 検索方式やEmbedding変更後に同じ評価を実行できる。
- 根拠が見つからない質問も評価ケースに含める。

---



## Epic 4: レッスンと基本問題の縦切り



### E4-01a Lesson・Question・Hintの入力スキーマを定義する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E2-04

完了条件:

- Lesson、Question、Hintの入力項目と制約が定義されている。
- 問題形式、正答、評価基準、出典、検証状態を表現できる。
- 線形結合レッスンの入力例がスキーマ検証を通る。



### E4-01b LessonのDBモデルを実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E1-04, E4-01a

完了条件:

- LessonとKC、教材参照の関係を保存・取得できる。
- 公開状態と入力スキーマの主要項目を保持できる。
- マイグレーションとモデルテストがある。



### E4-01c Question・HintのDBモデルを実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E1-04, E4-01a, E4-01b

完了条件:

- QuestionとHintをLesson、KCへ関連付けて保存・取得できる。
- 問題形式、正答、評価基準、出典、検証状態を保持できる。
- マイグレーションとモデルテストがある。



### E4-02 線形結合KCの基本レッスンを作成する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E2-03a, E3-02, E4-01a, E4-01b, E4-01c

完了条件:

- 学習目標、短い説明、具体例、教材参照がある。
- 計算問題、Explain-back問題、NumPy演習の雛形がある。
- 教材本文の長文転載を含まない。



### E4-03 KC一覧・レッスン取得APIを実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E2-06, E4-01b, E4-01c, E4-02

完了条件:

- KCから基本レッスンを取得できる。
- 学習目標、教材参照、問題、現在の学習状態を返せる。
- 存在しないKCと未公開レッスンを適切に扱う。



### E4-04a レッスン画面の情報設計とワイヤーフレームを決める

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E4-03

完了条件:

- KC、学習目標、教材、問題、ヒント、Masteryの配置が決まっている。
- PCと狭い画面の簡易ワイヤーフレームがある。
- 線形結合の一連の学習操作をワイヤーフレーム上で確認できる。



### E4-04b レッスン画面の基本構成を実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `L`
- Dependencies: E1-02, E4-03, E4-04a

完了条件:

- KC、学習目標、説明、数式、問題を表示できる。
- KaTeXで数式を表示できる。
- E4-04aのワイヤーフレームに沿ったレスポンシブ表示になっている。



### E4-05 PDF.jsによる教材ページ表示と出典移動を実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E3-03, E4-04b

完了条件:

- 教材PDFを表示できる。
- 出典から指定ページへ移動できる。
- ページ移動、拡大、縮小ができる。



### E4-06 固定回答・数値問題と段階的ヒントを実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `L`
- Dependencies: E4-01c, E4-04b

完了条件:

- 固定回答と数値回答を提出できる。
- 保存済み正答または確定的な処理で評価できる。
- 5段階ヒントを順に表示できる。
- 使用した最大ヒントレベルを記録できる。

---



## Epic 5: AIチューターとExplain-back



### E5-01 LLM Gatewayと構造化出力を実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E0-04, E1-01, E1-05

完了条件:

- LLM呼び出しを一つのバックエンド境界へまとめる。
- モデル名、用途、プロンプトバージョンを記録する。
- タイムアウトと不正な出力を処理できる。



### E5-02 出典付きRAG回答サービスを実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `L`
- Dependencies: E3-07, E5-01

完了条件:

- 現在のKCと質問から関連チャンクを検索する。
- LLMへ必要なチャンクだけを渡す。
- 教材に明記、教材から導出、AI補足を区別して返す。
- 教材名、ページ、チャンクIDを回答へ関連付ける。



### E5-03 根拠不足時の応答を実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `S`
- Dependencies: E5-02

完了条件:

- 関連チャンクがない場合に教材回答を捏造しない。
- 根拠不足であることと、質問を絞る方法を表示する。
- 外部Web検索を自動実行しない。



### E5-04 AI質問欄と出典表示を実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `L`
- Dependencies: E4-04b, E5-02, E5-03

完了条件:

- レッスン画面からAIへ質問できる。
- 回答と教材名・ページを表示できる。
- 教材回答とAI補足を区別して表示できる。
- エラーと待機状態を表示できる。



### E5-05 会話履歴と保存期間を実装する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `M`
- Dependencies: E5-02, E1-04

完了条件:

- 会話、対象KC、参照チャンク、モデル情報を保存する。
- 保存期間を設定値として管理する。
- 期限を過ぎた会話本文を削除できる。
- Masteryの根拠となる回答履歴は削除しない。



### E5-06 Explain-back評価を実装する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `L`
- Dependencies: E4-01c, E5-01

完了条件:

- 必須概念と評価基準をLLMへ渡す。
- 完全正解、軽微なミス、部分的正解、不正解へ正規化する。
- 不足概念、誤解、評価理由を保存・表示する。
- 代表回答を使った評価テストがある。



### E5-07 Socratic Modeの基本版を実装する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `M`
- Dependencies: E5-02, E5-04

完了条件:

- すぐに完全解答を出さず、段階的な問いを返せる。
- ユーザーが完全解答を求めた場合は拒否せず提示できる。
- 通常回答モードと切り替えられる。

---



## Epic 6: 回答履歴・Mastery・復習



### E6-01 Attempt・MasteryStateモデルを実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E1-04, E4-01c

完了条件:

- 回答、評価区分、評価点、ヒント、評価方法を保存できる。
- KCごとのMastery Score、状態、復習日時を保存できる。
- 計算方式とバージョンを保存できる。



### E6-02 Mastery Policy Version 1を実装する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `L`
- Dependencies: E6-01

完了条件:

- `docs/mastery-policy.md`のevidenceとMastery更新式を実装する。
- 未学習、学習中、習得、要復習を判定できる。
- 7つのポリシーテストケースが通る。
- 回答時間と問題難易度を計算に使用しない。



### E6-03 回答提出からMastery更新までを統合する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E4-06, E6-01, E6-02

完了条件:

- 回答評価、Attempt保存、Mastery更新を一連の処理として実行する。
- 同じ提出の重複処理を防ぐ。
- 更新前後のMasteryと評価理由を返す。



### E6-04 レッスン画面へ学習状態とフィードバックを表示する

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E4-04b, E6-03

完了条件:

- 現在のMasteryと状態を表示できる。
- 回答後に評価、ヒントの影響、更新後Masteryを表示できる。
- 次の学習活動または補習を案内できる。



### E6-05 復習間隔と優先度計算を実装する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `L`
- Dependencies: E6-02, E6-03

完了条件:

- `mastery-policy.md`の1、3、7、14、30、60日間隔を実装する。
- 復習成功、一部理解、失敗で次回日を更新できる。
- 期限、Mastery、誤答、ヒント、前提関係から優先度を計算できる。
- 優先度計算の単体テストがある。



### E6-06a 今日の復習APIを実装する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `M`
- Dependencies: E6-05, E4-06

完了条件:

- 今日の復習KCを優先度順に取得できる。
- KCごとの復習問題と現在のMasteryを返せる。
- 復習回答を既存の回答評価・Mastery更新処理へ渡せる。



### E6-06b 今日の復習画面を設計する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `M`
- Dependencies: E6-06a

完了条件:

- 復習一覧と回答画面の簡易ワイヤーフレームがある。
- 復習の開始、回答、結果確認、次の問題への遷移が決まっている。
- 今日の対象がない場合とAPIエラーの表示方法が決まっている。



### E6-06c 今日の復習画面を実装する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `M`
- Dependencies: E6-06a, E6-06b

完了条件:

- 復習問題、回答結果、次回復習日を表示できる。
- 今日の対象がない場合とAPIエラーを表示できる。



### E6-07 前回と異なる復習問題の選択を実装する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `M`
- Dependencies: E6-06a

完了条件:

- 直近と同じ問題を可能な限り避ける。
- 異なる問題形式または文脈を優先する。
- 候補がない場合のフォールバックがある。

---



## Epic 7: PyodideによるPython演習



### E7-01 Monaco EditorとPython演習UIを実装する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `M`
- Dependencies: E4-04b

完了条件:

- レッスン画面でPythonコードを編集できる。
- 実行、リセット、結果表示のUIがある。
- コードを実行するまで自動実行しない。



### E7-02 PyodideをWeb Workerで実行する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `L`
- Dependencies: E7-01

完了条件:

- PyodideをWorker内で初期化できる。
- 標準出力、戻り値、エラーをUIへ返せる。
- タイムアウト時にWorkerを終了できる。
- NumPy、SymPy、Matplotlibを許可リストから読み込める。



### E7-03 NumPy演習のテスト実行と採点を実装する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `L`
- Dependencies: E7-02, E4-01c

完了条件:

- 学習者コードと保存済みテストを実行できる。
- 成功、失敗、例外を共通の評価結果へ変換できる。
- 線形結合または行列ベクトル積の代表演習が動く。



### E7-04 Pythonコード回答を保存しMasteryへ反映する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `M`
- Dependencies: E6-03, E7-03

完了条件:

- コード、標準出力、エラー、テスト結果、実行環境を保存する。
- コード問題の評価をMastery更新へ渡せる。
- 保存したコードを表示するだけでは再実行しない。



### E7-05 Pyodide実行制限と出力安全性を確認する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `M`
- Dependencies: E7-02

完了条件:

- 実行時間、出力サイズ、描画データ量を制限する。
- 任意パッケージ取得と不要な外部通信を禁止する。
- 生成HTMLやSVGを未検証でアプリDOMへ挿入しない。
- 無限ループと過大出力のテストがある。

---



## Epic 8: MVP対象10 KCへの展開



### E8-01 線形結合以外の9 KCへレッスンを展開する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `XL`
- Dependencies: E2-03b, E2-05, E4-02, E6-04

完了条件:

- 残り9 KCに基本レッスンがある。
- 各レッスンに学習目標、説明、例、教材参照がある。
- 各レッスンの出典を確認している。

Issue化時は、線形結合のテンプレートを確認した後、2〜3 KC単位へ分割する。

### E8-02 MVP対象10 KCの確認問題とヒントを作成する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `XL`
- Dependencies: E4-06, E8-01

完了条件:

- 各KCに固定回答または数値問題がある。
- 各問題に正答、根拠、段階的ヒントがある。
- Mastery判定に使う主要問題を人間が確認している。



### E8-03 MVP対象KCへExplain-back問題を追加する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `XL`
- Dependencies: E5-06, E8-01

完了条件:

- 各KCに少なくとも一つのExplain-back問題がある。
- 必須概念、誤解例、評価基準がある。
- 代表回答による評価確認を行っている。



### E8-04 教材チャンクと10 KCの関連を登録・確認する

- Phase: `M2 MVP`
- Priority: `medium`
- Estimate: `XL`
- Dependencies: E2-03b, E3-05, E3-07

完了条件:

- StrangとGoodfellowの対象チャンクがKCへ関連付けられている。
- 関係種別とページ情報がある。
- KC指定検索で期待する教材箇所を取得できる。

---



## Epic 9: 品質確認と成果物



### E9-01a 線形結合の基本学習フローをEnd-to-Endでテストする

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E4-05, E6-04

完了条件:

- 問題、ヒント、回答保存、Mastery更新まで動作する。
- 教材の登録と出典ページへの移動が動作する。
- AI以外の確定的な処理を独立して再現・テストできる。
- 主要失敗ケースを含む自動テストまたは再現可能な確認手順がある。



### E9-01b 線形結合のAI学習フローをEnd-to-Endでテストする

- Phase: `M1 Vertical Slice`
- Priority: `high`
- Estimate: `M`
- Dependencies: E5-04, E9-01a

完了条件:

- PDF登録からチャンク生成、検索、出典付き質問まで動作する。
- 基本学習フローとAI質問を同じレッスンで利用できる。
- 主要失敗ケースを含む自動テストまたは再現可能な確認手順がある。



### E9-02 AI回答とRAG検索の品質確認を行う

- Phase: `M3 Polish`
- Priority: `low`
- Estimate: `M`
- Dependencies: E3-08, E5-02, E8-04

完了条件:

- 代表質問で回答と出典の対応を確認する。
- 根拠不足時に捏造しないことを確認する。
- AI補足と教材回答が区別されることを確認する。



### E9-03 セキュリティと著作権のMVPチェックリストを実行する

- Phase: `M3 Polish`
- Priority: `low`
- Estimate: `M`
- Dependencies: E3-03, E5-02, E7-05

完了条件:

- APIキーがフロントエンドとログへ出ていない。
- PDFと教材チャンクが意図せず公開されていない。
- 長文転載と無許可教材を避ける確認がある。
- ファイルアップロードとプロンプトインジェクションの代表ケースを確認する。



### E9-04 非機能要件の性能を測定する

- Phase: `M3 Polish`
- Priority: `low`
- Estimate: `M`
- Dependencies: E9-01b, E7-03

完了条件:

- レッスン表示、RAG検索、AI回答開始、採点、コード実行を計測する。
- `requirements.md`の目標との差を記録する。
- MVPで対処する問題と将来課題を分ける。



### E9-05 READMEとローカルデモ手順を完成させる

- Phase: `M3 Polish`
- Priority: `low`
- Estimate: `M`
- Dependencies: E9-01b

完了条件:

- プロジェクト目的、構成、セットアップ、起動、テスト方法がある。
- 教材PDFを含めずにデモ方法を説明している。
- ArchitectureとMastery Policyへのリンクがある。



### E9-06 MVPを自分で通して利用し、問題を記録する

- Phase: `M3 Polish`
- Priority: `low`
- Estimate: `XL`
- Dependencies: E6-06c, E7-04, E8-01, E8-02, E8-03

完了条件:

- 10 KCの主要レッスンを実際に利用する。
- RAG誤答、問題誤り、Mastery違和感、UI問題をIssue候補として記録する。
- `mastery-policy.md`の係数変更が必要か判断する。

---



## MVP後の候補

次はGitHub Projectsの`Later`または別の将来Projectで管理し、MVP Issueにはしない。

- Next.js App Routerへの移行
- Server Componentsの段階的導入
- キーワード検索とハイブリッド検索
- RAG再ランキング
- BKTおよびDeep Knowledge Tracing
- 高度なACT-R型スケジューリング
- 外部Web検索による教材補完
- PyTorch演習と隔離されたサーバー実行環境
- クラウドデプロイとオブジェクトストレージ
- 複数ユーザー、認証、教師用画面、課金
- PRML全体と追加分野への展開



## 残っている確認事項

1. PostgreSQL・pgvectorはDocker Composeで起動する方針でよいか。
2. Issue化は最初から全候補を登録するか、まず`M0 Foundation`と
   `M1 Vertical Slice`だけを登録するか。
3. 暫定採用するLLM・Embeddingプロバイダーは、実装開始時に候補を提示して
   短時間で決定する方針でよいか。
4. 会話履歴の具体的な保存期間は、AI機能を実装する段階で決めてよいか。
