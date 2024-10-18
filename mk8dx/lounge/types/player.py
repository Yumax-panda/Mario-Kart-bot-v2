from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from typing_extensions import NotRequired

__all__ = (
    "ReasonType",
    "MmrChange",
    "NameChange",
    "BasePlayer",
    "Player",
    "PartialPlayer",
    "PlayerDetails",
    "LeaderBoardPlayer",
)

if TYPE_CHECKING:
    from .rank import Rank
    from .tier import TierType

ReasonType = Literal[
    "Placement",
    "Table",
    "Penalty",
    "Strike",
    "Bonus",
    "TableDelete",
    "PenaltyDelete",
    "StrikeDelete",
    "BonusDelete",
]


class MmrChange(TypedDict):
    changeId: NotRequired[int | None]
    newMmr: int
    mmrDelta: int
    reason: ReasonType
    time: str
    score: NotRequired[int | None]
    partnerScores: NotRequired[list[int] | None]
    partnerIds: NotRequired[list[int] | None]
    tier: NotRequired[TierType | None]
    numTeams: NotRequired[int | None]


class NameChange(TypedDict):
    name: str
    changedOn: str


class BasePlayer(TypedDict):
    name: str
    mmr: NotRequired[int | None]


class Player(BasePlayer):
    id: int
    mkcId: int
    discordId: NotRequired[str | None]
    countryCode: NotRequired[str | None]
    switchFc: NotRequired[str | None]
    isHidden: bool
    maxMmr: NotRequired[int | None]
    linkedId: NotRequired[str | None]


class PartialPlayer(BasePlayer):
    mkcId: int
    eventsPlayed: int
    discordId: NotRequired[str | None]


class PlayerDetails(BasePlayer):
    playerId: int
    mkcId: int
    countryCode: NotRequired[str | None]
    countryName: NotRequired[str | None]
    switchFc: NotRequired[str | None]
    isHidden: bool
    season: int
    maxMmr: NotRequired[int | None]
    overallRank: NotRequired[int | None]
    eventsPlayed: int
    winRate: NotRequired[float | None]
    winsLastTen: int
    lossesLastTen: int
    gainLossLastTen: NotRequired[int | None]
    largestGain: NotRequired[int | None]
    largestGainTableId: NotRequired[int | None]
    largestLoss: NotRequired[int | None]
    largestLossTableId: NotRequired[int | None]
    averageScore: NotRequired[float | None]
    averageLastTen: NotRequired[float | None]
    partnerAverage: NotRequired[float | None]
    mmrChanges: list[MmrChange]
    nameHistory: list[NameChange]
    rank: str


class LeaderBoardPlayer(BasePlayer):
    id: int
    winsLastTen: int
    lossesLastTen: int
    eventsPlayed: int
    overallRank: NotRequired[int | None]
    countryCode: NotRequired[str | None]
    maxMmr: NotRequired[int | None]
    winRate: NotRequired[float | None]
    gainLossLastTen: NotRequired[int | None]
    largestGain: NotRequired[int | None]
    largestLoss: NotRequired[int | None]
    maxRank: NotRequired[Rank | None]
    maxMmrRank: NotRequired[Rank | None]
