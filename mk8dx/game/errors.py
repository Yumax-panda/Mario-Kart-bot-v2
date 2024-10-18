from utils.errors import BotError

__all__ = ("GameNotFound",)

GameNotFound = BotError(
    {
        "ja": "有効な即時情報が見つかりませんでした.",
        "en-US": "No valid game found.",
    }
)
