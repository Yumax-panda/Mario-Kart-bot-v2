from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

__all__ = ("LeaderBoard",)

if TYPE_CHECKING:
    from .player import LeaderBoardPlayer


class LeaderBoard(TypedDict):
    totalPlayers: int
    data: list[LeaderBoardPlayer]
