from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ApplicationContext, DiscordException
from discord.ext import commands

from utils.errors import BotError

from .core import Cog

if TYPE_CHECKING:
    from bot import Bot
    from utils.types import Context, HybridContext


class AdminCog(Cog, name="Admin", command_attrs=dict(hidden=True)):

    def __init__(self, bot: Bot) -> None:
        super().__init__(
            bot,
            description="Admin related",
            description_localizations={
                "ja": "管理者用",
                "en-US": "Admin related",
            },
            hidden=True,
        )

    async def cog_check(self, ctx: HybridContext) -> bool:  # type: ignore
        if not await self.bot.is_owner(ctx.author):  # type: ignore
            raise BotError(
                {
                    "ja": "このコマンドは管理者専用です。",
                    "en-US": "This command can only be executed by the Bot's owner.",
                }
            )
        return True

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: ApplicationContext, error: DiscordException) -> None:
        return await self.h.resolve_command_error(ctx, error)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: commands.CommandError) -> None:
        return await self.h.resolve_command_error(ctx, error)


def setup(bot: Bot) -> None:
    bot.add_cog(AdminCog(bot))
