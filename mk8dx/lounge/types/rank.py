from typing import Literal, TypedDict

from typing_extensions import NotRequired

__all__ = ("Division", "Rank")

Division = Literal[
    "Grandmaster",
    "Master",
    "Diamond",
    "Ruby",
    "Sapphire",
    "Platinum",
    "Gold",
    "Silver",
    "Bronze",
    "Iron",
    "Placement",
    "Unknown",
]


class Rank(TypedDict):
    division: Division
    level: NotRequired[int | None]
