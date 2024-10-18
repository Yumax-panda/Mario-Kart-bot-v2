from __future__ import annotations

import re
from typing import TYPE_CHECKING, Final, Iterable

__all__ = ("Rank",)

_SCORES: Final[tuple[int, ...]] = (15, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1)

# (全角文字のunicode, 半角文字)の辞書
_TRANSLATE_TABLE = dict(zip(map(ord, "１２３４５６７８９０ー＋　"), "1234567890-+ "))
_RANK_RE = re.compile(r"[^0-9\-\ +]")


class Rank:
    """ある1チームの1レース分の順位を表すクラス"""

    __slots__ = ("_data",)

    if TYPE_CHECKING:
        _data: list[int]

    def __init__(self, data: Iterable[int] = []) -> None:
        self._data = list(data)

    def __str__(self) -> str:
        return ",".join(map(str, sorted(self._data)))

    def __len__(self) -> int:
        return len(self.data)

    @property
    def data(self) -> list[int]:
        return self._data

    @property
    def score(self) -> int:
        return sum(map(lambda r: _SCORES[r - 1], self.data))
