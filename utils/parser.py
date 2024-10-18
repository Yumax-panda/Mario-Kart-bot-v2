from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, TypedDict

from utils.constants import get_offset

__all__ = (
    "parse_natural_numbers",
    "parse_integers",
    "get_hours",
    "get_friend_codes",
    "get_datetime",
    "maybe_param",
)

if TYPE_CHECKING:

    class DatetimeOptions(TypedDict, total=False):
        year: int
        month: int
        day: int
        hour: int

    class DiscordIdParam(TypedDict):
        discord_id: int

    class FriendCodeParam(TypedDict):
        fc: str

    class PlayerNameParam(TypedDict):
        name: str

    MaybeParam = DiscordIdParam | FriendCodeParam | PlayerNameParam


_NATURAL_NUMBER_RE = re.compile(r"\d+")
_INT_RE = re.compile(r"-?\d+")


# TODO: テストを書く
def parse_natural_numbers(string: str) -> list[int]:
    """自然数を文字列から全て抽出する.

    Parameters
    ----------
    string : str
        抽出元の文字列

    Returns
    -------
    list[int]
        抽出した自然数のリスト
    """
    return [int(match.group()) for match in _NATURAL_NUMBER_RE.finditer(string)]


def parse_integers(string: str) -> list[int]:
    """整数を文字列から全て抽出する.

    Parameters
    ----------
    string : str
        抽出元の文字列

    Returns
    -------
    list[int]
        抽出した整数のリスト
    """
    return [int(match.group()) for match in _INT_RE.finditer(string)]


_HOUR_RE = re.compile(r"\d+")
_HOUR_RANGE_RE = re.compile(r"(\d+)-(\d+)")


def get_hours(text: str) -> list[int]:
    """挙手時間を文字列から取得する。
    例えば, `19, 20`なら`[19, 20]`, `20-24`なら`[20, 21, 22, 23, 24]`を返す。

    Parameters
    ----------
    text : str
        挙手時間の文字列

    Returns
    -------
    list[int]
        挙手時間のリスト.

    Notes
    -----
    数字が大きすぎる場合, intへの変換でエラーが発生する可能性がある.
    """
    total: set[int] = set()

    for match in _HOUR_RANGE_RE.finditer(text):
        start, end = map(int, match.groups())
        if start > end:
            continue
        total.update(range(start, end + 1))

    for match in _HOUR_RE.finditer(text):
        total.add(int(match.group()))

    return sorted(total)


_FRIEND_CODE_RE = re.compile(r"\d{4}-\d{4}-\d{4}")


# TODO: テストを書く
def get_friend_codes(text: str) -> list[str]:
    """フレンドコードを文字列から取得する.
    \d{4}-\d{4}-\d{4}の形式にマッチする文字列を全て取得する.

    Parameters
    ----------
    text : str
        フレンドコードの文字列

    Returns
    -------
    list[str]
        フレンドコードのリスト
    """
    return [match.group() for match in _FRIEND_CODE_RE.finditer(text)]


def get_datetime(text: str, locale: str | None) -> datetime | None:
    """文字列から日時を取得する.足りない情報は現在の日時とlocaleから推測する.

    Parameters
    ----------
    text : str
        日時の文字列. 例: "2021-10-01 12", "10-01 12", "12"
        分は指定することができない.
    locale : str | None
        ロケール

    Returns
    -------
    datetime | None
        日時. パースに失敗した場合はNoneを返す.
    """
    numbers = parse_natural_numbers(text)
    now = datetime.now() + timedelta(hours=get_offset(locale))
    options: DatetimeOptions = {
        "day": now.day,
        "month": now.month,
        "year": now.year,
        "hour": now.hour,
    }

    if len(numbers) == 0:
        return None

    if len(numbers) == 1 and 0 <= numbers[0] <= 23:
        options["hour"] = numbers[0]
    elif len(numbers) == 2 and 1 <= numbers[0] <= 31 and 0 <= numbers[1] <= 23:
        options["day"], options["hour"] = numbers
    elif len(numbers) == 3 and 1 <= numbers[0] <= 12 and 1 <= numbers[1] <= 31 and 0 <= numbers[2] <= 23:
        options["month"], options["day"], options["hour"] = numbers
    elif (
        len(numbers) == 4
        and 2000 <= numbers[0] < now.year + 1
        and 1 <= numbers[1] <= 12
        and 1 <= numbers[2] <= 31
        and 0 <= numbers[3] <= 23
    ):
        options["year"], options["month"], options["day"], options["hour"] = numbers
    else:
        return None

    return datetime(**options)


# TODO: test
def maybe_param(text: str) -> MaybeParam:
    """テキストからユーザー情報を識別するためのパラメータを取得する.
    主にAPIにリクエストするときに指定する`params`に使用する.

    フレンドコード, Discord IDのいずれでもない場合はプレイヤー名として扱う.

    Parameters
    ----------
    text : str
        パラメータを取得するテキスト.

    Returns
    -------
    MaybeParam
        パラメータ.
    """

    if friend_codes := get_friend_codes(text):
        return {"fc": friend_codes[0]}

    if discord_ids := parse_natural_numbers(text):
        return {"discord_id": discord_ids[0]}

    return {"name": text}
