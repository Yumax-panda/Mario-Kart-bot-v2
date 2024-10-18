from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

__all__ = ("ResultRepository",)

if TYPE_CHECKING:
    from datetime import datetime

    from model.results import ResultItem, ResultItemWithID, Results


class ResultRepository(metaclass=ABCMeta):
    @abstractmethod
    async def create_result(
        self,
        guild_id: int,
        played_at: datetime,
        score: int,
        enemy: str,
        enemy_score: int,
    ) -> None:
        """指定したサーバーの戦績を追加する.

        Parameters
        ----------
        guild_id : int
            戦績を登録するサーバーのID.
        played_at : datetime
            対戦日時. (JST)
        score : int
            自チームの得点.
        enemy : str
            相手チームの名前.
        enemy_score : int
            相手チームの得点.
        """
        ...

    @abstractmethod
    async def get_result(self, guild_id: int, result_id: int) -> ResultItem | None:
        """指定したサーバーの戦績を取得する.

        Parameters
        ----------
        guild_id : int
            サーバーのID.
        result_id : int
            戦績のID.

        Returns
        -------
        ResultItem | None
            戦績. 戦績が存在しない場合はNone.
        """

    @abstractmethod
    async def delete_result(self, guild_id: int, result_id: int) -> None:
        """
        指定したサーバーの戦績を削除する.

        Parameters
        ----------
        guild_id : int
            サーバーのID.
        result_id : int
            戦績のID.
        """
        ...

    @abstractmethod
    async def update_result(
        self,
        guild_id: int,
        result_id: int,
        played_at: datetime | None = None,
        score: int | None = None,
        enemy: str | None = None,
        enemy_score: int | None = None,
    ) -> None:
        """
        指定したサーバーの戦績を更新する.
        Noneが渡された場合は更新しない.

        Parameters
        ----------
        guild_id : int
            サーバーのID.
        result_id : int
            戦績のID.
        played_at : datetime | None
            対戦日時. (JST)
        score : int | None
            自チームの得点.
        enemy : str | None
            相手チームの名前.
        enemy_score : int | None
            相手チームの得点.
        """
        ...

    @abstractmethod
    async def put_results(self, guild_id: int, results: Results) -> None:
        """指定したギルドの戦績を上書きする.

        Parameters
        ----------
        guild_id : int
            ギルドのID
        results : Results
            戦績のリスト. 戦績は日付の昇順でソートされている必要がある.
        """
        ...

    @abstractmethod
    async def get_results(self, guild_id: int) -> list[ResultItemWithID]:
        """指定したギルドの戦績を取得する. 対戦日時の古い順にソートされている.

        Parameters
        ----------
        guild_id : int
            ギルドのID

        Returns
        -------
        list[ResultItemWithID]
            戦績のリスト
        """
        ...
