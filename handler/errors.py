from __future__ import annotations

from typing import TYPE_CHECKING

from utils.constants import MAX_EMBED_FIELDS, MAX_ROLES, MAX_SELECT_OPTIONS
from utils.errors import BotError

__all__ = (
    "BookmarkLimitExceeded",
    "EnemyNameNotFound",
    "FailedToGetBotData",
    "FailedToGetMemberData",
    "GuildNotFound",
    "InvalidCSVFile",
    "InvalidDatetimeInput",
    "InvalidGameMessage",
    "InvalidScoreInput",
    "LoginRequired",
    "NoBookmarkRegistered",
    "NoFriendCodeFound",
    "NoMembersAvailable",
    "NoParametersSpecified",
    "NoPlayerFound",
    "NotCSVFile",
    "NotGathering",
    "NoViewablePlayers",
    "QueriedResultNotFound",
    "ResultNotFound",
    "TimeNotSelected",
    "TeamNameNotSet",
    "TimeOutOfRange",
    "TooManyFriendCodes",
    "TooManyRoles",
    "TooManyTimeSelected",
)

if TYPE_CHECKING:
    from utils.constants import LocaleDict


class EnemyNameNotFound(BotError):
    """相手チーム名で絞り込んで戦績データを検索した際, 戦績が見つからなかった場合のエラー."""

    def __init__(self, similar_names: list[str]) -> None:
        message: LocaleDict = {
            "ja": f"該当するチーム名が見つかりませんでした.",
            "en-US": f"Team name not found.",
        }

        if similar_names:
            lineup = ", ".join(similar_names)
            message["ja"] += f" 似た名前: {lineup}"
            message["en-US"] += f" Similar names: {lineup}"

        super().__init__(message)


# なるべくアルファベット順に並べる
BookmarkLimitExceeded = BotError(
    {
        "ja": f"ブックマークは{MAX_SELECT_OPTIONS}個までしか登録できません",
        "en-US": f"You can only bookmark up to {MAX_SELECT_OPTIONS} players",
    }
)

FailedToGetBotData = BotError(
    {
        "ja": "Bot情報の取得に失敗しました",
        "en-US": "Failed to get bot data",
    }
)

FailedToGetMemberData = BotError(
    {
        "ja": "メンバー情報の取得に失敗しました",
        "en-US": "Failed to get member data",
    }
)


GuildNotFound = BotError(
    {
        "ja": "サーバー情報を取得できませんでした",
        "en-US": "Failed to get guild data",
    }
)

InvalidCSVFile = BotError(
    {
        "ja": "CSVファイルの形式が正しくありません",
        "en-US": "Invalid CSV file format",
    }
)

InvalidDatetimeInput = BotError(
    {
        "ja": "日付は`HH`, `DD HH`, `MM/DD HH`, `YYYY/MM/DD HH` の形式で入力してください",
        "en-US": "Please enter the date in the format of `HH`, `DD HH`, `MM/DD HH`, `YYYY/MM/DD HH`",
    }
)

InvalidGameMessage = BotError(
    {
        "ja": "即時のメッセージではありません.",
        "en-US": "Not a sokuji message.",
    }
)

InvalidScoreInput = BotError(
    {
        "ja": "<自チームの得点> <相手チームの得点: 省略可能> の形式で入力してください. 例: `10 5`",
        "en-US": "Please enter in the format of <your team's score> <opponent team's score: optional>. Example: `10 5`",
    }
)

LoginRequired = BotError(
    {
        "ja": "Nintendo Switch Onlineのログインが必要です. `/friend setup`を実行してください.",
        "en-US": "Nintendo Switch Online login is required. Please run `/friend setup`.",
    }
)

NoBookmarkRegistered = BotError(
    {
        "ja": "ブックマークされたプレイヤーが見つかりませんでした",
        "en-US": "No bookmarked players found",
    }
)

NoFriendCodeFound = BotError(
    {
        "ja": "フレンドコードが見つかりませんでした",
        "en-US": "No friend code found",
    }
)

NoMembersAvailable = BotError(
    {
        "ja": "メンバーが見つかりませんでした",
        "en-US": "No members available  ",
    }
)

NoParametersSpecified = BotError(
    {
        "ja": "少なくとも一つ以上のパラメータを指定してください",
        "en-US": "Please specify at least one parameter",
    }
)

NoPlayerFound = BotError(
    {
        "ja": "プレイヤーが見つかりませんでした",
        "en-US": "Player not found",
    }
)

NotCSVFile = BotError(
    {
        "ja": "CSVファイルを添付してください",
        "en-US": "Please attach a CSV file",
    }
)


NotGathering = BotError(
    {
        "ja": "現在募集している時間はありません",
        "en-US": "There is no gathering time currently being recruited",
    }
)

NoViewablePlayers = BotError(
    {
        "ja": "閲覧可能なプレイヤーが見つかりませんでした",
        "en-US": "No players found",
    }
)

QueriedResultNotFound = BotError(
    {
        "ja": "指定された戦績が見つかりませんでした",
        "en-US": "The specified result was not found",
    }
)

ResultNotFound = BotError(
    {
        "ja": "戦績が見つかりませんでした",
        "en-US": "Result not found",
    }
)

TeamNameNotSet = BotError(
    {
        "ja": "チーム名が登録されていません",
        "en-US": "Team name is not set",
    }
)


TimeNotSelected = BotError(
    {
        "ja": "時間が選択されていません",
        "en-US": "Time is not selected",
    }
)

TimeOutOfRange = BotError(
    {
        "ja": "時間は0から48の間で指定してください",
        "en-US": "Please select a time between 0 and 48",
    }
)

TooManyFriendCodes = BotError(
    {
        "ja": "入力されたフレンドコードが多すぎます",
        "en-US": "Too many friend codes entered",
    }
)

TooManyRoles = BotError(
    {
        "ja": f"ロールは{MAX_ROLES}個までしか登録できません",
        "en-US": f"You can only register up to {MAX_ROLES} roles",
    }
)

TooManyTimeSelected = BotError(
    {
        "ja": f"時間は{MAX_EMBED_FIELDS}個までしか選択できません",
        "en-US": f"You can only select up to {MAX_EMBED_FIELDS} times",
    }
)
