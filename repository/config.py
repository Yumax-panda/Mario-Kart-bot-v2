from __future__ import annotations

import ssl
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import create_async_engine

from model.core import metadata

from .repository import Repository

__all__ = ("Config",)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


class Config:

    if TYPE_CHECKING:
        user: str
        password: str
        host_name: str
        port: int
        db_name: str
        ssl_ca_path: str | None

    def __init__(
        self, user: str, password: str, host_name: str, port: int, db_name: str, ssl_ca_path: str | None = None
    ) -> None:
        self.user = user
        self.password = password
        self.host_name = host_name
        self.port = port
        self.db_name = db_name
        self.ssl_ca_path = ssl_ca_path

    @property
    def dsn(self) -> str:
        return f"mysql+aiomysql://{self.user}:{self.password}@{self.host_name}:{self.port}/{self.db_name}"

    def create_engine(self, *, echo: bool = True) -> AsyncEngine:
        """接続設定からエンジンを作成する."""
        connect_args = {}

        if self.ssl_ca_path:
            connect_args["ssl"] = ssl.create_default_context(cafile=self.ssl_ca_path)

        return create_async_engine(
            self.dsn,
            echo=echo,
            pool_pre_ping=True,
            connect_args=connect_args,
        )

    async def get_repository(self) -> Repository:
        engine = self.create_engine()

        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

        return Repository(engine)
