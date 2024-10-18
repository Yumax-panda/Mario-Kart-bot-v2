from __future__ import annotations

from typing import TYPE_CHECKING

__all__ = (
    "format_scores",
    "format_banner_user_name",
    "user_mention",
    "format_result_datetime",
    "win_or_lose",
)

if TYPE_CHECKING:
    from datetime import datetime as dt

    from discord import Member, User


def format_scores(scores: list[int], compact: bool = False) -> str:
    """得点を表す文字列を作成する.

    Parameters
    ----------
    scores : list[int]
        [自チーム, 相手チーム]の得点のリスト.
    compact : bool, optional
        コンパクトな表示形式にするかどうか, by default False

    Returns
    -------
    str
        得点を表す文字列
    """
    if not len(scores) == 2:
        raise ValueError("scores must have 2 elements")
    return " : ".join(map(str, scores)) + ("({:+})".format(scores[0] - scores[1]) if not compact else "")


def format_banner_user_name(user: Member | User) -> str:
    """OBSバナー利用者の名前を表す文字列を作成する.

    Parameters
    ----------
    user : Member | User
        ユーザー

    Returns
    -------
    str
        ユーザー名
    """
    return (user.name + user.discriminator).replace(" ", "")


def user_mention(id: int | str) -> str:
    """ユーザーIDをメンション形式に変換する.

    Parameters
    ----------
    id : int | str
        ユーザーID

    Returns
    -------
    str
        メンション形式の文字列
    """
    return f"<@{id}>"


def format_result_datetime(datetime: dt) -> str:
    """戦績の日時は文字列として保存されるため, datetimeから文字列に変換する関数.

    Parameters
    ----------
    datetime : dt
        戦績を表す日時

    Returns
    -------
    str
        戦績の日時を表す文字列
    """
    fmt = "%Y-%m-%d %H:%M:%S"
    return datetime.strftime(fmt)


def win_or_lose(diff: int) -> str:
    """勝敗を表す文字列を作成する.

    Parameters
    ----------
    diff : int
        得点の差

    Returns
    -------
    str
        勝敗を表す文字列
    """
    if diff < 0:
        return "Lose"
    elif diff == 0:
        return "Draw"
    return "Win"
