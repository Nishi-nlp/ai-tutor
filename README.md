# AI Tutor

Knowledge Component（KC）を中心に、教材参照、AIとの対話、問題演習、
Mastery更新、復習を統合する個人利用向けAIチューターです。

現在はMVPの設計と開発基盤を整備しています。MVPの技術構成は
React + TypeScript + Vite、FastAPI、PostgreSQL + pgvectorです。

## ディレクトリ構成

| パス | 用途 |
|---|---|
| `apps/frontend/` | React + TypeScript + Viteフロントエンド |
| `apps/backend/` | FastAPIバックエンド |
| `data/books/` | 開発時に参照する教材PDF |
| `data/kcs/` | レビュー済みKCデータ |
| `docs/` | 要件、Architecture、Mastery Policy、Backlog |
| `schemas/` | KC、Lesson、Questionなどのスキーマ |
| `scripts/` | 教材抽出、KC生成・検証・登録用スクリプト |
| `tests/fixtures/pdfs/` | Git管理可能なCC0のPDFテストデータ |

`apps/frontend/`、`apps/backend/`、`schemas/`の具体的な内容は、
対応するIssueで段階的に追加します。

## Git管理方針

- ソースコード、スキーマ、レビュー済みKC、設計文書を管理する。
- OSファイル、Pythonキャッシュ、依存パッケージ、ビルド成果物は管理しない。
- `.env`など秘密情報を含むファイルは管理しない。
- 共有が必要な環境変数は、値を空またはダミーにした`.env.example`で管理する。
- 個人所有またはダウンロードした教材PDFはGit管理しない。
- PDF処理のテストには、プロジェクト作成のCC0サンプルを使用する。

## ローカル開発構成

MVP開発では、フロントエンドとバックエンドをホスト上で起動し、
PostgreSQLとpgvectorだけをDocker Composeで起動します。

| サービス | 起動場所 | 開発ポート |
|---|---|---:|
| React + Vite | ホスト | `5173` |
| FastAPI + Uvicorn | ホスト | `8000` |
| PostgreSQL + pgvector | Docker Compose | ホスト`5433`からコンテナ`5432`へ接続 |

ReactとFastAPIをホストで起動することで、ホットリロードとデバッグを
簡単にします。PostgreSQLとpgvectorはDocker化し、OSごとの導入差を
なくします。GitHubでアプリケーションを配布する段階では、全サービスを
Docker Composeで起動できる構成を別途追加します。

### 環境変数

- ルートの`.env`はDocker ComposeとFastAPIが共有する。Git管理しない。
- ルートの`.env.example`は変数名とローカル開発用ダミー値を記載し、Git管理する。
- `apps/frontend/.env.local`はViteのローカル設定に使用し、Git管理しない。
- `apps/frontend/.env.example`はフロントエンド用のサンプルとしてGit管理する。
- `VITE_`で始まる変数はブラウザへ公開されるため、秘密情報を設定しない。
- LLMやEmbeddingのAPIキーは、プロバイダー決定後にルートの`.env`へ追加する。

初回はサンプルをコピーして、必要に応じてローカル値を変更します。

```console
cp .env.example .env
cp apps/frontend/.env.example apps/frontend/.env.local
```

### 教材PDF

個人所有またはダウンロードした教材PDFは`data/books/`へ配置します。
このディレクトリ内のPDFはGit管理せず、Dockerイメージにも含めません。
PostgreSQLにはPDF本体ではなく、保存先、チェックサム、ページ情報などの
メタデータを保存します。

テストでは`tests/fixtures/pdfs/sample-linear-algebra.pdf`を使用します。
これはプロジェクトが作成し、CC0 1.0で提供する3ページのサンプルです。
次のコマンドで再生成できます。

```console
uv run --with reportlab python scripts/generate_sample_pdf.py
```

## ローカル開発手順

次のコマンドはリポジトリのルートで実行します。React、FastAPI、
PostgreSQLの実体は後続Issueで初期化するため、それまでは起動できません。

### 1. PostgreSQLとpgvectorを起動する

```console
docker compose up -d db
```

PostgreSQLには`localhost:5433`で接続します。コンテナ内では標準ポートの
`5432`を使用します。pgvector拡張はDB初期化時に有効化します。

### 2. FastAPIを起動する

初回または依存関係の更新後に同期します。

```console
uv sync --project apps/backend
```

開発サーバーを起動します。`--reload`により、Pythonコードの変更時に
サーバーが自動再起動します。

```console
uv run --project apps/backend uvicorn --app-dir apps/backend app.main:app \
  --reload --port 8000 --env-file .env
```

### 3. Reactを起動する

初回または依存関係の更新後にパッケージをインストールします。

```console
npm --prefix apps/frontend install
```

Vite開発サーバーを起動します。Reactの変更はブラウザへ即時反映されます。

```console
npm --prefix apps/frontend run dev -- --port 5173
```

ブラウザで`http://localhost:5173`を開きます。FastAPIは
`http://localhost:8000`、APIドキュメントは`http://localhost:8000/docs`
で確認します。

### 4. 終了する

ReactとFastAPIは、それぞれ起動したターミナルで`Ctrl+C`を押します。
DBを終了する場合は次を実行します。

```console
docker compose down
```

`docker compose down`では名前付きDBボリュームを保持します。
ローカルデータも削除する`--volumes`は、意図して初期化する場合だけ使用します。

## 品質チェック

Pull Requestを作成・更新する前に、リポジトリのルートで次の確認を行います。
初回または依存関係の更新後は、先にロックファイルどおりの依存関係を
インストールします。

```console
npm --prefix apps/frontend ci
uv sync --directory apps/backend --frozen
```

### フロントエンド

```console
npm --prefix apps/frontend run lint
npm --prefix apps/frontend run format:check
npm --prefix apps/frontend run test
npm --prefix apps/frontend run build
```

コードをPrettierで整形する場合は、次を実行します。

```console
npm --prefix apps/frontend run format
```

### バックエンド

```console
uv run --directory apps/backend ruff check .
uv run --directory apps/backend ruff format --check .
uv run --directory apps/backend python -m pytest
```

コードをRuffで整形する場合は、次を実行します。

```console
uv run --directory apps/backend ruff format .
```

`format:check`と`ruff format --check`はファイルを変更せず、整形が必要な場合に
失敗します。整形コマンドを実行した後は、lint、format、testをもう一度
実行してください。

### Pull Requestの品質ゲート

GitHub Actionsでは、Pull Requestの作成・更新時にFrontendとBackendを
別々のジョブとして検査します。Pull Requestを完了扱いにするには、次を
すべて満たす必要があります。

- ローカルのフロントエンドとバックエンドの品質チェックがすべて成功している。
- GitHub ActionsのFrontendとBackendが両方とも成功している。
- 失敗したチェックを無効化、削除またはスキップして回避していない。

いずれかのCIジョブが失敗または実行中の場合、その変更は完了扱いにせず、
Pull Requestをマージしません。失敗時はGitHub Actionsの該当ジョブとステップの
ログを確認し、原因を修正してpushした後、新しい実行が成功することを確認します。

## ドキュメント

- [要件定義](docs/requirements.md)
- [Architecture](docs/architecture.md)
- [Mastery Policy](docs/mastery-policy.md)
- [Backlog候補](docs/backlog-candidates.md)
