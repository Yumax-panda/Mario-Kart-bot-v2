from typing import Literal, TypedDict

from typing_extensions import NotRequired

__all__ = (
    "WellKnownDivision",
    "UnknownDivision",
    "Division",
    "Rank",
)

WellKnownDivision = Literal[
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
]

UnknownDivision = Literal["Placement", "Unknown"]

Division = Literal[WellKnownDivision, UnknownDivision]


class Rank(TypedDict):
    division: Division
    level: NotRequired[int | None]
