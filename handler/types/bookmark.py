from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

__all__ = ("BookmarkHandler",)

if TYPE_CHECKING:
    from discord import ApplicationContext

    from utils.types import HybridContext


class BookmarkHandler(metaclass=ABCMeta):
    @abstractmethod
    async def bookmark_stats(self, ctx: HybridContext) -> None:
        """ブックマークされたプレイヤーのStatsを表示する.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        """
        ...

    @abstractmethod
    async def bookmark_add(self, ctx: ApplicationContext, player_name: str, nick: str | None) -> None:
        """ブックマークを追加する.

        Parameters
        ----------
        ctx : ApplicationContext
            コマンドのコンテキスト.
        player_name : str
            ブックマークしたいプレイヤーの名前.
        nick : str | None
            ニックネーム. None の場合は player_name がそのままニックネームとして登録される.
        """
        ...

    @abstractmethod
    async def bookmark_remove(self, ctx: ApplicationContext) -> None:
        """ブックマークを削除する. 削除するためのViewを送信する.

        Parameters
        ----------
        ctx : ApplicationContext
            コマンドのコンテキスト.
        """
        ...
