from utils.errors import BotError

__all__ = (
    "FailedToGetAccessToken",
    "FailedToGetFToken",
    "FailedToGetNintendoSwitchAccount",
    "FailedToGetSessionToken",
    "FailedToGetUserInfo",
    "FailedToGetVersion",
    "FailedToLogin",
    "FailedToSendFriendRequest",
)

# なるべくアルファベット順に並べる

FailedToGetAccessToken = BotError(
    {
        "ja": "アクセストークンの取得に失敗しました",
        "en-US": "Failed to get access token",
    }
)

# これはユーザーが見るエラーメッセージだから, 直にFTokenという名前を出すべきではない
FailedToGetFToken = BotError(
    {
        "ja": "認証情報の取得に失敗しました",
        "en-US": "Failed to get authentication information",
    }
)


FailedToGetNintendoSwitchAccount = BotError(
    {
        "ja": "Nintendo Switchアカウントの取得に失敗しました",
        "en-US": "Failed to get Nintendo Switch account",
    }
)

FailedToGetSessionToken = BotError(
    {
        "ja": "セッショントークンの取得に失敗しました",
        "en-US": "Failed to get session token",
    }
)

FailedToGetUserInfo = BotError(
    {
        "ja": "ユーザー情報の取得に失敗しました",
        "en-US": "Failed to get user info",
    }
)

FailedToGetVersion = BotError(
    {
        "ja": "バージョン情報の取得に失敗しました",
        "en-US": "Failed to get version information",
    }
)


FailedToLogin = BotError(
    {
        "ja": "ログインに失敗しました",
        "en-US": "Failed to login",
    }
)

FailedToSendFriendRequest = BotError(
    {
        "ja": "フレンドリクエストの送信に失敗しました",
        "en-US": "Failed to send friend request",
    }
)
