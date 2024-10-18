from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Iterable

__all__ = ("GatherRepository",)

if TYPE_CHECKING:
    from model.gathers import GatherItem, ParticipationType


class GatherRepository(metaclass=ABCMeta):
    @abstractmethod
    async def insert_gathers(
        self,
        guild_id: int,
        user_ids: Iterable[int],
        type: ParticipationType,
        hours: Iterable[int],
    ) -> None:
        """挙手情報を登録する.

        Parameters
        ----------
        guild_id : int
            サーバーのID.
        user_ids : Iterable[int]
            挙手したユーザーのID.
        type : ParticipationType
            挙手の種類.
        hours : Iterable[int]
            挙手した時間.
        """
        ...

    @abstractmethod
    async def delete_gathers(
        self,
        guild_id: int,
        user_ids: Iterable[int],
        hours: Iterable[int],
    ) -> None:
        """指定したユーザーの指定した時間の挙手情報を削除する.

        Parameters
        ----------
        guild_id : int
            サーバーのID.
        user_ids : Iterable[int]
            挙手を削除するユーザーのID.
        hours : Iterable[int]
            挙手を削除する時間.
        """
        ...

    @abstractmethod
    async def delete_all_gathers_by_hours(self, guild_id: int, hours: Iterable[int]) -> None:
        """指定したサーバーの指定した時間の挙手情報を全て削除する.

        Parameters
        ----------
        guild_id : int
            サーバーのD.
        hours : Iterable[int]
            削除する挙手情報の時間.
        """
        ...

    @abstractmethod
    async def clear_gathers(self, guild_id: int) -> None:
        """指定したサーバーの挙手情報を全て削除する.

        Parameters
        ----------
        guild_id : int
            サーバーのID.
        """
        ...

    @abstractmethod
    async def get_all_gathers(self, guild_id: int) -> list[GatherItem]:
        """挙手情報を取得する.

        Parameters
        ----------
        guild_id : int
            サーバーのID.

        Returns
        -------
        list[GatherItem]
            挙手情報.
        """
        ...
