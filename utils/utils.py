from collections import OrderedDict
from typing import Any, Callable, Iterable, NoReturn, TypeVar

from .errors import BotError

__all__ = (
    "drop_duplicates",
    "get_average",
    "deprecated",
    "under_construction",
    "under_maintenance",
)

T = TypeVar("T")
KeyT = TypeVar("KeyT")


def drop_duplicates(data_with_key: Iterable[tuple[KeyT, T]]) -> list[tuple[KeyT, T]]:
    """キーが重複している場合、最初の要素のみを残して重複を削除する.

    Parameters
    ----------
    data_with_key : Iterable[tuple[KeyT, T]]
        キーが重複している可能性のあるデータ. KeyTで等しいかどうかを判断する.

    Returns
    -------
    list[tuple[KeyT, T]]
        重複を削除したデータ.
    """
    data: OrderedDict[KeyT, T] = OrderedDict()

    for key, value in data_with_key:
        if key not in data:
            data[key] = value

    return list(data.items())


def get_average(
    data: Iterable[T],
    key: Callable[[T], int | float | None],
) -> int | float | None:
    """指定されたキーによって取得された値の平均を返す.

    Parameters
    ----------
    data : Iterable[T]
        平均を計算したいデータ.
    key : Callable[[T], int  |  float  |  None]
        データから取得したい値を返す関数.

    Returns
    -------
    int | float | None
        平均値. データがない場合はNone.
    """
    valid: list[int | float] = []

    for v in data:
        value = key(v)

        if value is not None:
            valid.append(value)

    if not valid:
        return None

    return sum(valid) / len(valid)


def deprecated(*args: Any, **kwargs: Any) -> NoReturn:
    """廃止された関数を表す.

    Parameters
    ----------
    *args, **kwargs : Any
        何もしない.
    """
    raise BotError({"ja": "この機能は廃止されました.", "en-US": "This function has been deprecated."})


def under_construction(*args: Any, **kwargs: Any) -> NoReturn:
    """作成中の関数を表す.

    Parameters
    ----------
    *args, **kwargs : Any
        何もしない.
    """
    raise BotError({"ja": "この機能は現在開発中です.", "en-US": "This function is under construction."})


def under_maintenance(*args: Any, **kwargs: Any) -> NoReturn:
    """メンテナンス中の関数を表す.

    Parameters
    ----------
    *args, **kwargs : Any
        何もしない.
    """
    raise BotError({"ja": "この機能は現在メンテナンス中です.", "en-US": "This function is currently under maintenance."})
