from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from typing_extensions import NotRequired

__all__ = ("Score", "Team", "Table")

if TYPE_CHECKING:
    from .tier import TierType


class Score(TypedDict):
    score: int
    multiplier: float
    playerId: int
    playerName: str
    playerDiscordId: NotRequired[str]
    playerCountryCode: NotRequired[str]
    delta: NotRequired[int]
    prevMmr: NotRequired[int]
    newMmr: NotRequired[int]


class Team(TypedDict):
    rank: int
    scores: list[Score]


class Table(TypedDict):
    id: int
    season: int
    createdOn: str
    verifiedOn: NotRequired[str]
    deletedOn: NotRequired[str]
    numTeams: int
    url: str
    tier: TierType
    teams: list[Team]
    tableMessageId: NotRequired[str]
    updateMessageId: NotRequired[str]
    authorId: NotRequired[str]
