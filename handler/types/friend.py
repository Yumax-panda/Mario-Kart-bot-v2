from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, overload

__all__ = ("FriendHandler",)

if TYPE_CHECKING:
    from discord import ApplicationContext

    from utils.types import Context, HybridContext


class FriendHandler(metaclass=ABCMeta):

    @overload
    async def friend_mmr(
        self,
        ctx: Context,
        *,
        text: str,
        ascending: bool | None = None,
    ) -> None: ...
    @overload
    async def friend_mmr(
        self,
        ctx: ApplicationContext,
        *,
        text: str,
        ascending: bool | None = None,
        view_original: bool = True,
    ) -> None: ...
    @abstractmethod
    async def friend_mmr(
        self,
        ctx: HybridContext,
        *,
        text: str,
        ascending: bool | None = None,
        view_original: bool = True,
    ) -> None:
        """フレンドコードを抽出し, プレイヤーの平均MMRを表示する.
        (fm: friend code MMR)

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        text : str
            MMRを含むテキスト.
        ascending : bool | None, optional
            昇順にするかどうか. Falseなら降順, Noneの場合はもとの並び順, by default None
        view_original : bool, optional
            入力されたテキストを出力と合わせて表示するかどうか, by default True
        """
        ...

    @overload
    async def friend_peak_mmr(
        self,
        ctx: Context,
        *,
        text: str,
        ascending: bool | None = None,
    ) -> None: ...
    @overload
    async def friend_peak_mmr(
        self,
        ctx: ApplicationContext,
        *,
        text: str,
        ascending: bool | None = None,
        view_original: bool = True,
    ) -> None: ...
    @abstractmethod
    async def friend_peak_mmr(
        self,
        ctx: HybridContext,
        *,
        text: str,
        ascending: bool | None = None,
        view_original: bool = True,
    ) -> None:
        """MMRを抽出し, プレイヤーのMMRのピークを表示する.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        text : str
            MMRを含むテキスト.
        ascending : bool | None, optional
            昇順にするかどうか. Falseなら降順, Noneの場合はもとの並び順, by default None
        view_original : bool, optional
            入力されたテキストを出力と合わせて表示するかどうか, by default True
        """
        ...
