# AI Tutor — 7日版

`la.linear_combination`（線形結合）1つに対象を絞り、教材登録から学習履歴と
Mastery更新までを縦に通すAIチューターの技術検証です。

```text
教材登録 → チャンク・Embedding生成 → レッスン表示
→ 教材根拠付きAI質問 → 問題・ヒント → 採点
→ Mastery更新 → 学習履歴の保存
```

## 7日版のスコープ

必須:

- Next.js App Router + TypeScriptの学習画面
- FastAPI、PostgreSQL、pgvector、SQLAlchemy、Alembic
- CC0サンプルPDFの登録、ページ単位の抽出、Embedding、類似検索
- 教材名・ページ番号を示すAI回答と、根拠不足時の回答抑止
- 固定回答または数値問題2問、3段階以上のヒント、採点
- 回答履歴の保存と簡易Mastery Scoreの更新
- 主要フローのテスト、デモ手順、スクリーンショット、60〜90秒の動画

対象外:

- 複数KC、認証、複数ユーザー、クラウド公開
- OCR、マルチモーダル解析、高度なRAG、汎用PDF対応
- Socratic Mode、Explain-back評価、Python演習、本格的な復習機能
- 本番運用水準のセキュリティ、性能、可用性

完成時は「完成した製品版MVP」ではなく、
「Next.js・FastAPI・pgvectorによる線形結合1KCの学習フローの技術検証」
として説明します。

## 技術構成

| レイヤー | 採用技術 |
|---|---|
| Frontend | Next.js App Router + TypeScript |
| Backend | FastAPI |
| Database | PostgreSQL + pgvector |
| ORM / Migration | SQLAlchemy + Alembic |
| LLM / Embedding | バックエンドの環境変数でモデルを指定 |

LLM APIキーはブラウザへ渡しません。教材PDFは公開ディレクトリ外へ保存し、
LLMへ送るチャンクは回答に必要な最小範囲に限定します。

> 現在の`apps/frontend/`は旧Vite雛形です。Day 1の`E1-02-7D`で
> Next.js App Routerへ置き換えます。現時点の雛形を完成版として扱いません。

## ディレクトリ

| パス | 用途 |
|---|---|
| `apps/frontend/` | Next.jsフロントエンド（Day 1で移行） |
| `apps/backend/` | FastAPIバックエンド |
| `data/kcs/` | レビュー済みKCデータ |
| `data/books/` | Git管理しない教材PDFの保存先 |
| `docs/` | 7日版の要件、設計、計画、Mastery方針 |
| `scripts/` | 教材・KCの生成、検証、登録用スクリプト |
| `tests/fixtures/pdfs/` | Git管理可能なCC0サンプルPDF |

## 開発環境の目標構成

| サービス | 起動場所 | ポート |
|---|---|---:|
| Next.js | ホスト | `3000` |
| FastAPI | ホスト | `8000` |
| PostgreSQL + pgvector | Docker Compose | `5433` → `5432` |

目標とする起動手順はDay 1で実装・検証し、このREADMEへ確定版を反映します。
未実装のコマンドを動作済みとしては記載しません。

## 環境変数の方針

- ルート`.env`にDB接続、LLM、Embeddingの秘密情報を置き、Git管理しない。
- コミットする`.env.example`には変数名と安全なダミー値だけを置く。
- Next.jsでブラウザ公開する値だけ`NEXT_PUBLIC_`を付ける。
- APIキーには`NEXT_PUBLIC_`を付けず、FastAPIだけから参照する。
- モデル名は設定値として保存し、Embeddingには使用モデル名も記録する。

## 7日間の実装計画

- Day 1: Next.js、FastAPI、PostgreSQL、pgvector、Alembic
- Day 2: KC、レッスン、問題、回答履歴、Mastery
- Day 3: 一画面の学習UI
- Day 4: PDF登録、抽出、チャンク、Embedding、検索
- Day 5: 教材根拠付きAI質問と出典表示
- Day 6: 統合テスト、安全性、UI調整
- Day 7: README、デモ、スクリーンショット、動画、予備時間

詳細は[7日版ToDo](docs/mvp-todo.md)を参照してください。

## 完了条件

- READMEの確定手順でローカル起動できる。
- Next.js上で線形結合のレッスン、問題、ヒント、採点を利用できる。
- CC0 PDFからチャンクとEmbeddingを生成し、教材根拠付きで質問できる。
- AI回答に教材名とページを表示し、根拠不足時は推測しない。
- 回答履歴とMasteryがDBへ保存され、再読み込み後も保持される。
- バックエンドの主要テストとNext.jsの本番ビルドが成功する。
- スクリーンショットと60〜90秒の動画で一連の動作を説明できる。

## ドキュメント

- [7日版要件](docs/requirements.md)
- [7日版Architecture](docs/architecture.md)
- [7日版ToDo](docs/mvp-todo.md)
- [Issue一覧・依存関係](docs/backlog-candidates.md)
- [Mastery Policy](docs/mastery-policy.md)
