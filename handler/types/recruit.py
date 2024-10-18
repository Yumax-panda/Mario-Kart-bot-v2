from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Sequence

__all__ = ("RecruitHandler",)

if TYPE_CHECKING:
    from discord import Role

    from utils.types import HybridContext, HybridMember


class RecruitHandler(metaclass=ABCMeta):
    @abstractmethod
    async def can(self, ctx: HybridContext, members: Sequence[HybridMember], target: str) -> None:
        """指定した時間で挙手する.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        members : Sequence[HybridMember]
            参加するメンバー.
        target : str
            挙手する時間.
            例えば, `19, 20`や`20-24`のような形式.
        """
        ...

    @abstractmethod
    async def tentative(self, ctx: HybridContext, members: Sequence[HybridMember], target: str) -> None:
        """指定した時間で仮挙手する.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        members : Sequence[HybridMember]
            参加するメンバー.
        target : str
            挙手する時間.
            例えば, `19, 20`や`20-24`のような形式.
        """
        ...

    @abstractmethod
    async def substitute(self, ctx: HybridContext, members: Sequence[HybridMember], target: str) -> None:
        """指定した時間で補欠として挙手する.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        members : Sequence[HybridMember]
            参加するメンバー.
        target : str
            挙手する時間.
            例えば, `19, 20`や`20-24`のような形式.
        """
        ...

    @abstractmethod
    async def drop(self, ctx: HybridContext, members: Sequence[HybridMember], target: str) -> None:
        """指定した時間で挙手を取り消す.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        members : Sequence[HybridMember]
            参加するメンバー.
        target : str
            挙手する時間.
            例えば, `19, 20`や`20-24`のような形式.
        """
        ...

    @abstractmethod
    async def clear(self, ctx: HybridContext) -> None:
        """挙手を全て取り消す.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        """
        ...

    @abstractmethod
    async def out(self, ctx: HybridContext, target: str) -> None:
        """指定した時間で挙手を全て取り消す.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        target : str
            挙手する時間.
            例えば, `19, 20`や`20-24`のような形式.
        """
        ...

    @abstractmethod
    async def now(self, ctx: HybridContext) -> None:
        """現在の挙手状況を表示する.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        """
        ...

    @abstractmethod
    async def pick(self, ctx: HybridContext, role: Role) -> None:
        """指定した役職のメンバーからランダムに選び、メンションする.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        role : Role
            メンバーを選出するロール.
        """
        ...
