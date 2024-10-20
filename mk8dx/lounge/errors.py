from utils.errors import BotError

__all__ = (
    "NoMMRFound",
    "PlacementPlayer",
    "UnknownPlayer",
)


class LoungeError(BotError):
    pass


NoMMRFound = LoungeError(
    {
        "ja": "プレイヤーのMMR情報がありません.",
        "en-US": "No MMR found.",
    },
)

PlacementPlayer = LoungeError(
    {
        "ja": "このプレイヤーはPlacementにつき, MMR情報がありません.",
        "en-US": "This player is in Placement, so there is no MMR information.",
    }
)

UnknownPlayer = LoungeError(
    {
        "ja": "不明なプレイヤーです.",
        "en-US": "This player is unknown.",
    }
)
