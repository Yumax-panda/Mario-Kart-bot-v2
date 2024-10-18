from __future__ import annotations

from typing import TYPE_CHECKING

from .repository import Repository

__all__ = ("Config",)


class Config:

    if TYPE_CHECKING:
        user: str
        password: str
        host_name: str
        port: int | str
        db_name: str

    def __init__(
        self,
        user: str,
        password: str,
        host_name: str,
        port: int | str,
        db_name: str,
    ) -> None:
        self.user = user
        self.password = password
        self.host_name = host_name
        self.port = port
        self.db_name = db_name

    @property
    def dsn(self) -> str:
        return f"mysql+aiomysql://{self.user}:{self.password}@{self.host_name}:{self.port}/{self.db_name}"

    async def get_repository(self, url: str | None = None) -> Repository:
        return await Repository.setup(url or self.dsn)
