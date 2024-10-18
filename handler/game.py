from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ApplicationContext

from mk8dx.game import Game

from .errors import GuildNotFound
from .types import BaseHandler as IBaseHandler, GameHandler as IGameHandler

__all__ = ("GameHandler",)

if TYPE_CHECKING:
    from discord import Role

    from utils.types import HybridContext


class GameHandler(IBaseHandler, IGameHandler):
    async def game_start(self, ctx: HybridContext, enemy: str, role: Role | None) -> None:
        if isinstance(ctx, ApplicationContext):
            await ctx.defer()

        if (guild := ctx.guild) is None:
            raise GuildNotFound

        team_name: str = await self.repo.get_team_name(guild.id) or guild.name  # type: ignore
        members = role.members if role else []

        await Game.start(ctx, [team_name, enemy], members)
