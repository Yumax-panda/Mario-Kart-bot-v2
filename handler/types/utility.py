from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

__all__ = ("UtilityHandler",)

if TYPE_CHECKING:
    from discord import ApplicationContext

    from utils.constants import Locale
    from utils.types import HybridContext


class UtilityHandler(metaclass=ABCMeta):
    @abstractmethod
    async def help(self, ctx: ApplicationContext, locale: Locale | None = None) -> None:
        """ヘルプコマンド.

        Parameters
        ----------
        ctx : ApplicationContext
            コマンドのコンテキスト.
        locale : Locale
            ヘルプの言語.
        """
        ...

    @abstractmethod
    async def link(self, ctx: HybridContext, name: str) -> None:
        """指定したラウンジ名をもつプレイヤーの情報とコマンドを呼び出したユーザーの情報を紐付ける.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        name : str
            ラウンジ名.
        """
        ...
