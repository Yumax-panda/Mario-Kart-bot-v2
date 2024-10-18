from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ApplicationContext, OptionChoice, option, slash_command

from .core import Cog

if TYPE_CHECKING:
    from bot import Bot
    from utils.constants import Locale


class UtilityCog(Cog, name="Utility"):

    def __init__(self, bot: Bot) -> None:
        super().__init__(
            bot,
            description="Utility functions",
            description_localizations={
                "ja": "便利機能",
                "en-US": "Utility functions",
            },
        )

    @slash_command(name="help", description="Show help message", description_localizations={"ja": "コマンドの使い方"})
    @option(
        name="language",
        type=str,
        parameter_name="locale",
        name_localizations={"ja": "言語"},
        description="Language",
        description_localizations={"ja": "言語"},
        choices=[
            OptionChoice(name="Japanese", value="ja", name_localizations={"ja": "日本語"}),
            OptionChoice(name="English", value="en-US"),
        ],
        default=None,
    )
    async def help(self, ctx: ApplicationContext, locale: Locale | None = None) -> None:
        return await self.h.help(ctx, locale)

    @slash_command(
        name="link",
        description="Link to another account used in lounge server.",
        description_localizations={"ja": "ラウンジサーバーに入っているアカウントと連携"},
    )
    @option(
        name="player_name",
        type=str,
        name_localizations={"ja": "ラウンジ名"},
        description="Player name to link.",
        description_localizations={"ja": "連携するプレイヤー名"},
    )
    async def link(self, ctx: ApplicationContext, player_name: str) -> None:
        return await self.h.link(ctx, player_name)


def setup(bot: Bot) -> None:
    bot.add_cog(UtilityCog(bot))
