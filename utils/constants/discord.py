from discord import Color

__all__ = (
    "MAX_EMBED_FIELDS",
    "MAX_ROLES",
    "MAX_SELECT_OPTIONS",
    "EmbedColor",
)

MAX_EMBED_FIELDS = 25
MAX_ROLES = 250
MAX_SELECT_OPTIONS = 25


class EmbedColor:
    default = Color.yellow()
    error = Color.red()
    archive = Color(0x00BFFF)
