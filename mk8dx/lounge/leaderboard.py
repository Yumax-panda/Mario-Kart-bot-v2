from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, SupportsIndex, overload

from .player import LeaderBoardPlayer
from .utils import BaseModel

__all__ = ("LeaderBoard",)

if TYPE_CHECKING:
    from .types.leaderboard import LeaderBoard as LeaderBoardPayload


class LeaderBoard(BaseModel):

    __slots__ = ("total_players", "data")

    if TYPE_CHECKING:
        totalPlayers: int
        data: list[LeaderBoardPlayer]

    def __init__(self, data: LeaderBoardPayload) -> None:
        self.total_players = data["totalPlayers"]
        self.data = [LeaderBoardPlayer(item) for item in data["data"]]

    def to_dict(self) -> LeaderBoardPayload:
        return {
            "totalPlayers": self.total_players,
            "data": [item.to_dict() for item in self.data],
        }

    @property
    def is_empty(self) -> bool:
        return len(self.data) == 0

    @overload
    def __getitem__(self, index: SupportsIndex) -> LeaderBoardPlayer: ...
    @overload
    def __getitem__(self, index: slice) -> list[LeaderBoardPlayer]: ...
    def __getitem__(self, index: SupportsIndex | slice) -> LeaderBoardPlayer | list[LeaderBoardPlayer]:
        return self.data[index]

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator[LeaderBoardPlayer]:
        return iter(self.data)
