from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

__all__ = ("Cog",)

if TYPE_CHECKING:
    from bot import Bot
    from handler.types.handler import Handler as IHandler
    from utils.constants import LocaleDict


class Cog(commands.Cog):
    if TYPE_CHECKING:
        bot: Bot
        description: str
        description_localizations: LocaleDict
        hidden: bool

    def __init__(
        self,
        bot: Bot,
        description: str,
        description_localizations: LocaleDict,
        hidden: bool = False,
    ) -> None:
        self.bot = bot
        self.description = description
        self.description_localizations = description_localizations
        self.hidden = hidden

    @property
    def h(self) -> IHandler:
        """コマンドの処理を行うハンドラを返す.
        `self.bot.h`のショートカット.

        Returns
        -------
        Handler
            コマンドの処理を行うハンドラ
        """
        return self.bot.h
