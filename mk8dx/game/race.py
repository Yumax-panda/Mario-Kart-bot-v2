from __future__ import annotations

from typing import TYPE_CHECKING

from .rank import Rank

__all__ = ("Race",)

if TYPE_CHECKING:
    from .track import Track


class Race:
    __slots__ = ("_ranks", "track")

    if TYPE_CHECKING:
        _ranks: list[Rank]
        track: Track | None

    def __init__(self, ranks: list[Rank], track: Track | None = None):
        self._ranks = ranks
        self.track = track

    @property
    def ranks(self) -> list[Rank]:
        return self._ranks

    @property
    def scores(self) -> list[int]:
        return [r.score for r in self.ranks]
