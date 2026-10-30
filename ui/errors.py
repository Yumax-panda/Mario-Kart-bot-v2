from utils.errors import BotError

__all__ = (
    "FailedToGetUserData",
    "InvalidMessage",
    "MessageNotFound",
    "PlayerNotFound",
    "PlayerNotSelected",
)


class UIError(BotError):
    pass


class ViewError(UIError):
    pass


FailedToGetUserData = UIError(
    {
        "ja": "ユーザー情報の取得に失敗しました.",
        "en-US": "Failed to get user data.",
    },
)


InvalidMessage = ViewError(
    {
        "ja": "無効なメッセージです.",
        "en-US": "Invalid message.",
    },
)

MessageNotFound = ViewError(
    {
        "ja": "メッセージが見つかりませんでした.",
        "en-US": "Message not found.",
    },
)

PlayerNotFound = ViewError(
    {
        "ja": "プレイヤーが見つかりませんでした.",
        "en-US": "Player not found.",
    },
)


PlayerNotSelected = ViewError(
    {
        "ja": "プレイヤーが選択されていません.",
        "en-US": "Player not selected.",
    },
)
