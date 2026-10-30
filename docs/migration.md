# マイグレーション

データベースのスキーマは[Alembic](https://alembic.sqlalchemy.org/)で管理する。

## 構成

- `alembic.ini` : Alembic本体の設定。接続情報はここには書かず、`migrations/env.py` が環境変数から組み立てる。
- `migrations/env.py` : マイグレーションの実行環境。`model/` 配下の全モジュールを読み込み、`metadata` に登録されたテーブルを比較対象にする。
  - Botの起動時は、`Repository.migrate()` から渡された接続を使う。
  - CLIの実行時は、`-x db_url=...`、なければ `DB_*` 環境変数から `Config.create_engine()` でエンジンを作成する。
- `migrations/versions/` : リビジョンファイル。

## コマンド

いずれも `DB_USERNAME` / `DB_PASSWORD` / `DB_HOSTNAME` / `DB_PORT` / `DB_NAME` / `SSL_CA_PATH` を参照する。`.env` があれば読み込み、未設定の項目はローカル用の既定値を使う。

| コマンド | 内容 |
| --- | --- |
| `poetry run task migrate -m "reason"` | モデルとの差分から新しいリビジョンを生成する。 |
| `poetry run task upgrade` | 未適用のマイグレーションをすべて適用する。 |
| `poetry run task downgrade` | 直近のマイグレーションを1つ巻き戻す。 |
| `poetry run task stamp` | DDLを実行せず、DBを `head` 適用済みとして記録する。 |
| `poetry run task migrate-check` | モデルとDBに差分がないか確認する。 |
| `poetry run task migrate-history` | リビジョン履歴と現在の適用バージョンを表示する。 |

接続先は環境変数で切り替える。

```bash
DB_HOSTNAME=example.com DB_PORT=4000 DB_NAME=mkbot poetry run task migrate-check
```

`stamp` と `check` は接続URLでも指定できる。パスワードの記号はパーセントエンコードする。TLSが必要なDBでは、クエリの `ssl_ca` にCA証明書のパスを指定する。省略すると `SSL_CA_PATH` を参照する。

```bash
make stamp url="mysql://user:pass@example.com:4000/mkbot?ssl_ca=/etc/ssl/cert.pem"
make check url="mysql://user:pass@example.com:4000/mkbot?ssl_ca=/etc/ssl/cert.pem"
```

## 運用

### 起動時の自動マイグレーション

Botの起動時に `Config.get_repository()` から `Repository.migrate()` が呼ばれ、未適用のマイグレーションが `head` まで適用される。通常は手動で `task upgrade` を実行する必要はない。

### スキーマ変更の手順

1. `model/` 配下のモデルを編集する。
2. `poetry run task migrate -m "変更内容"` でリビジョンを生成する。
3. 生成された `migrations/versions/*.py` が意図どおりの差分になっているか確認する。
4. ローカルで `poetry run task upgrade` を実行し、適用できることを確認する。
5. リビジョンファイルをコミットする。

### 既存DBへの導入

`metadata.create_all` で作られたDBには `alembic_version` テーブルがない。そのまま起動すると初期リビジョンの `CREATE TABLE` が実行され、`Table 'gathers' already exists` で起動に失敗する。

新しいコードをデプロイする前に、次の手順を一度だけ実行する。

1. 削除済みのフレンド申請機能のテーブルが残っていれば削除する。

   ```sql
   DROP TABLE IF EXISTS session_tokens, nso_tokens, requests;
   ```

2. 対象のDBに `poetry run task stamp` を実行する。
3. `poetry run task migrate-check` で差分がないことを確認する。

手順1を省くと `task migrate-check` で差分が検出され、そのDBに対して `task migrate` を実行するとこれらのテーブルを削除するリビジョンが生成される。

起動に失敗したあとでも、同じ手順で復旧できる。失敗時には空の `alembic_version` テーブルだけが作られており、スキーマは変更されない。
