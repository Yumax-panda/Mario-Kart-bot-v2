from __future__ import annotations

from typing import TYPE_CHECKING

__all__ = ("get_offset",)

if TYPE_CHECKING:
    from utils.constants import Locale


def get_offset(locale: str | None) -> int:
    """タイムゾーンのオフセットを取得する.

    Parameters
    ----------
    locale : Locale | None
        ロケール.

    Returns
    -------
    int
        UTCとのオフセット. localeが登録されていない場合は0を返す.
    """

    data: dict[Locale, int] = {
        "ja": 9,
        "en-US": -7,
    }

    return data.get(locale, 0)  # type: ignore
