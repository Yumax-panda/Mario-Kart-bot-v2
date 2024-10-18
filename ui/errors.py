from utils.errors import BotError

__all__ = (
    "FailedToGetUserData",
    "InvalidMessage",
    "InvalidAuthURI",
    "InvalidTextInput",
    "MessageNotFound",
    "NintendoSwitchAccountIDNotFound",
    "PlayerNotFound",
    "PlayerNotSelected",
)


class UIError(BotError):
    pass


class ViewError(UIError):
    pass


class ModalError(UIError):
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

InvalidTextInput = ModalError(
    {
        "ja": "無効な入力です.",
        "en-US": "Invalid input.",
    },
)

InvalidAuthURI = ModalError(
    {
        "ja": "無効な認証URLです.",
        "en-US": "Invalid auth URI.",
    },
)

NintendoSwitchAccountIDNotFound = ViewError(
    {
        "ja": "Nintendo Switch AccountのIDを取得できませんでした.",
        "en-US": "Failed to get Nintendo Switch Account ID.",
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
