from typing import Final, Literal

__all__ = (
    "MIN_SEASON",
    "CURRENT_SEASON",
    "Season",
)

Season = Literal[4, 5, 6, 7, 8, 9, 10, 11]
MIN_SEASON: Final[int] = 4
CURRENT_SEASON: Final[int] = 11
