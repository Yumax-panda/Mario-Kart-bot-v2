import asyncio
import importlib
import os
import pkgutil
from logging.config import fileConfig
from urllib.parse import parse_qs, urlsplit

from alembic import context
from sqlalchemy.engine import Connection

import model
from model.core import metadata
from repository import Config

try:
    import _config
except ImportError:
    pass

config = context.config

if config.config_file_name is not None and config.attributes.get("connection") is None:
    fileConfig(config.config_file_name)

for module in pkgutil.iter_modules(model.__path__):
    importlib.import_module(f"{model.__name__}.{module.name}")

target_metadata = metadata


def _build_config() -> Config:
    """`-x db_url=...`, なければDB_*環境変数から接続設定を作成する."""
    db_url = context.get_x_argument(as_dictionary=True).get("db_url")

    if db_url:
        url = urlsplit(db_url)
        ssl_ca = parse_qs(url.query).get("ssl_ca", [None])[0]
        # Config.dsnはURLへそのまま埋め込むので, パーセントエンコードは解除しない.
        return Config(
            user=url.username or "",
            password=url.password or "",
            host_name=url.hostname or "",
            port=url.port or 3306,
            db_name=url.path.lstrip("/"),
            ssl_ca_path=ssl_ca or os.environ.get("SSL_CA_PATH") or None,
        )

    return Config(
        user=os.environ.get("DB_USERNAME", "root"),
        password=os.environ.get("DB_PASSWORD", "password"),
        host_name=os.environ.get("DB_HOSTNAME", "localhost"),
        port=int(os.environ.get("DB_PORT", "3306")),
        db_name=os.environ.get("DB_NAME", "mkbot"),
        ssl_ca_path=os.environ.get("SSL_CA_PATH") or None,
    )


def run_migrations_offline() -> None:
    """DBへ接続せずにSQLを出力する."""
    context.configure(
        url=_build_config().dsn,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """渡された接続でマイグレーションを実行する."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """環境変数から作成したエンジンでマイグレーションを実行する."""
    engine = _build_config().create_engine(echo=False)

    async with engine.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


def run_migrations_online() -> None:
    """アプリから渡された接続, なければ新しいエンジンでマイグレーションを実行する."""
    connection = config.attributes.get("connection", None)

    if connection is not None:
        do_run_migrations(connection)
    else:
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
