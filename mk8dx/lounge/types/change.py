from typing import TypedDict

from typing_extensions import NotRequired

__all__ = ("_ChangeBase", "Bonus", "Penalty")


class _ChangeBase(TypedDict):
    id: int
    season: int
    awardedOn: str
    prevMmr: int
    newMmr: int
    amount: int
    deletedOn: NotRequired[str]
    playerId: int
    playerName: str


class Bonus(_ChangeBase): ...


class Penalty(_ChangeBase):
    isStrike: bool
