from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

__all__ = ("PinnedPlayerRepository",)

if TYPE_CHECKING:
    from model.pinned_players import PinnedPlayer, PinnedPlayerItem


class PinnedPlayerRepository(metaclass=ABCMeta):
    @abstractmethod
    async def put_pinned_player(self, user_id: int, player_id: int, nick_name: str) -> None:
        """ブックマークされたプレイヤーの情報を保存する.

        Parameters
        ----------
        user_id : int
            ブックマークを保存するユーザーのID.
        player_id : int
            保存するプレイヤーのID.
        nick_name : str
            保存するプレイヤーのニックネーム.
        """
        ...

    @abstractmethod
    async def delete_pinned_player(self, user_id: int, player_id: int) -> None:
        """ブックマークされたプレイヤーの情報を削除する.

        Parameters
        ----------
        user_id : int
            ブックマークを削除するユーザーのID.
        player_id : int
            削除するプレイヤーのID.
        """
        ...

    @abstractmethod
    async def get_pinned_players(self, user_id: int) -> list[PinnedPlayer]:
        """ブックマークされたプレイヤーの情報を取得する.

        Parameters
        ----------
        user_id : int
            ブックマークを取得するユーザーのID.

        Returns
        -------
        list[PinnedPlayer]
            ブックマークされたプレイヤーの情報.
        """
        ...
