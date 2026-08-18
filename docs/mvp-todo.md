# AI Tutor 7日版 ToDo

## ゴール

`la.linear_combination`について、教材登録から学習履歴保存までの縦切りを
ローカルでデモできる状態にする。技術構成はNext.js App Router、FastAPI、
PostgreSQL + pgvector、SQLAlchemy、Alembicとする。

## Day 1 — Next.js・FastAPI・DB基盤

- [x] `E0-01-7D` 要件、Architecture、README、ToDoを7日版へ統一する
- [ ] `E0-03-7D` Next.js・FastAPI・DBの起動方法と環境変数を確定する
- [ ] `E1-01-7D` FastAPIの構成、ヘルスチェック、APIテストを整備する
- [ ] `E1-02-7D` Vite雛形をNext.js App Router + TypeScriptへ置き換える
- [ ] `E1-02-7D` 学習ルート、APIクライアント、loading/errorを用意する
- [x] `E1-03-7D` PostgreSQL + pgvectorをComposeで起動しFastAPIから接続する
- [x] `E1-04-7D` SQLAlchemy、Alembic、初期migrationを導入する

完了条件: Next.js、FastAPI、PostgreSQLを起動でき、画面から`GET /health`を
呼べてpgvectorが有効になっている。

## Day 2 — KC・レッスン・問題・Mastery

- [ ] `E2-01-7D` 線形結合KCのYAML、学習目標、前提KCを確定する
- [ ] `E2-02-7D` KC YAMLの必須項目と前提KCを検証する
- [ ] `E2-04-7D` KnowledgeComponentモデルを実装する
- [ ] `E2-05-7D` KCを冪等にDB登録する
- [ ] `E2-06-7D` KC詳細APIを実装する
- [ ] `E4-01a-7D` Lesson・Question・Hintスキーマを定義する
- [ ] `E4-01b-7D` Lesson・Question・Hintモデルを実装する
- [ ] `E4-02-7D` 説明・具体例・確認問題を含むレッスンを作る
- [ ] `E4-06-7D` 2問、3段階以上のヒント、採点を実装する
- [ ] `E6-01-7D` Attempt・MasteryStateモデルを実装する
- [ ] `E6-02-7D` evidenceとMastery更新式、単体テストを実装する
- [ ] `E6-03-7D` 採点、履歴保存、Mastery更新を接続する

完了条件: DBからKCとレッスンを取得し、回答によって履歴とMasteryを
同一トランザクションで更新できる。

## Day 3 — 学習画面

- [ ] `E4-04a-7D` 一画面の情報設計を決める
- [ ] `E4-04b-7D` 目標、前提、説明、例、問題、ヒントを表示する
- [ ] `E4-06-7D` 回答をFastAPIへ送り、正誤と理由を表示する
- [ ] `E6-04-7D` Masteryの現在値、変化、次の行動を表示する
- [ ] Server Componentで初期取得し、操作部分だけClient Componentにする
- [ ] スマートフォン幅、loading、error、空状態を確認する

完了条件: Next.js上で問題、ヒント、採点、Mastery更新が動き、再読み込み後も
Masteryが保持される。

## Day 4 — 教材登録と簡易RAG

- [ ] `E3-02-7D` Document・DocumentChunkモデルと非公開保存を実装する
- [ ] `E3-03-7D` PDF、MIME、サイズを検証する登録APIを実装する
- [ ] `E3-04-7D` CC0教材をページ単位で抽出してチャンク化する
- [ ] `E3-06-7D` Embeddingを生成し、モデル名とともにpgvectorへ保存する
- [ ] `E3-07-7D` KCで絞った類似検索と根拠不足判定を実装する
- [ ] `E3-08-7D` 代表質問と期待出典を3件用意する

完了条件: PDFからチャンクとEmbeddingを生成し、検索結果から教材名、ページ、
チャンクIDを追跡できる。

## Day 5 — AIチューターと出典

- [ ] `E5-01-7D` LLM呼び出しをサービス層へ分離し構造化出力を検証する
- [ ] `E5-02-7D` 検索チャンクを根拠に回答と出典を生成する
- [ ] `E5-02-7D` 教材記載、教材から導出、AI補足を区別する
- [ ] `E5-03-7D` 根拠不足とLLM障害を安全に処理する
- [ ] `E5-04-7D` AI質問欄、状態表示、出典、二重送信防止を実装する

完了条件: 教材に基づいて質問でき、教材名とページを表示し、根拠不足時は
推測回答を生成しない。

## Day 6 — 統合テスト・安全性・UI

- [ ] `E9-01a-7D` 問題からMasteryまでの統合テストを追加する
- [ ] `E9-01b-7D` 教材登録から出典付きAI回答までの統合テストを追加する
- [ ] `E9-02-7D` 期待出典、根拠不足、AI補足区分を確認する
- [ ] `E9-03-7D` APIキー、PDF保存、アップロード、注入、長文転載を確認する
- [ ] デスクトップとスマートフォン幅の主要操作を確認する
- [ ] 空、loading、error、Mastery変化、出典の表示を調整する

完了条件: 主要フローのテストが通り、代表的な失敗を安全に扱え、デモ操作で
迷わない画面になっている。

## Day 7 — README・デモ・予備時間

- [ ] `E9-05-7D` 目的、構成、セットアップ、起動、テスト、デモ手順を書く
- [ ] 実装済み、簡略化、未実装、技術選定理由、ロードマップを書く
- [ ] 新しい環境を想定してREADMEどおりに起動する
- [ ] lint、test、Next.js本番ビルドを実行する
- [ ] デモ用PDF、質問、期待回答を確認する
- [ ] 主要画面のスクリーンショットを撮る
- [ ] 60〜90秒のデモ動画を作る
- [ ] APIキーを含むファイルがGit管理されていないことを確認する

## 最終完了条件

- [ ] READMEどおりにローカル起動できる
- [ ] 線形結合のレッスン、問題、ヒント、採点が動く
- [ ] PDF登録、Embedding、検索、出典付きAI質問が動く
- [ ] 根拠不足時に捏造しない
- [ ] 履歴とMasteryが保存され、再読み込み後も保持される
- [ ] 主要バックエンドテストとNext.js本番ビルドが成功する
- [ ] スクリーンショットとデモ動画で説明できる

## 時間が余った場合だけ

KC一覧・簡易マップ、PDF.js、AI会話履歴、復習日、復習画面、ブラウザE2E、
性能計測、GitHub Actions、ダークモード。

## 7日版ではやらない

残り9KC、OCR、マルチモーダル解析、高度なRAG、Explain-back、Socratic Mode、
Python演習、本格的な復習、認証、複数ユーザー、クラウド公開、本番監査。
