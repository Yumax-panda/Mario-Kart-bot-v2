from utils.errors import BotError

__all__ = ("NoMMRFound",)


class LoungeError(BotError):
    pass


NoMMRFound = LoungeError(
    {
        "ja": "プレイヤーのMMR情報がありません.",
        "en-US": "No MMR found.",
    },
)
