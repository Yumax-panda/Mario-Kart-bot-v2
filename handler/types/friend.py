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

    @abstractmethod
    async def friend_setup(self, ctx: ApplicationContext) -> None:
        """フレンド申請ができるようにする.

        Parameters
        ----------
        ctx : ApplicationContext
            コマンドのコンテキスト.
        """
        ...

    @abstractmethod
    async def friend_request(self, ctx: ApplicationContext, code: str, private: bool) -> None:
        """フレンド申請を送信する.

        Parameters
        ----------
        ctx : ApplicationContext
            コマンドのコンテキスト.
        code : str
            フレンドコード, discord_id, ラウンジ名のいずれか.
        private : bool
            自分だけ申請を送れるようにするかどうか.
        """
        ...

    @abstractmethod
    async def text_friend_request(self, ctx: Context, *, code: str) -> None:
        """フレンド申請を送信する.

        Parameters
        ----------
        ctx : Context
            コマンドのコンテキスト.
        code : str
            フレンドコード, discord_id, ラウンジ名のいずれか.
        """
        ...

    @abstractmethod
    async def friend_code(self, ctx: ApplicationContext, private: bool) -> None:
        """自分のフレンドコードを表示する.

        Parameters
        ----------
        ctx : ApplicationContext
            コマンドのコンテキスト.
        private : bool
            自分だけ表示するかどうか.
        """
        ...

    @abstractmethod
    async def friend_multiple(self, ctx: ApplicationContext, codes: str, private: bool) -> None:
        """複数のフレンド申請を一括で送信する.

        Parameters
        ----------
        ctx : ApplicationContext
            コマンドのコンテキスト.
        codes : str
            フレンドコードが含まれる文.
        private : bool
            自分だけ申請を送れるようにするかどうか.
        """
        ...
