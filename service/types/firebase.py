from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Literal, TypedDict

__all__ = (
    "GamePayload",
    "FirebaseService",
)


class GamePayload(TypedDict):
    diff: str
    left: int
    scores: list[int]
    teams: list[str]
    win: Literal[0, 1]


class FirebaseService(metaclass=ABCMeta):
    @abstractmethod
    def update_game_data(self, data: dict[str, GamePayload]) -> None:
        """Firebase Realtime Databaseに保存された即時のデータを更新する.

        Parameters
        ----------
        data : dict[str, GamePayload]
            新しい即時のデータ
        """
        ...
