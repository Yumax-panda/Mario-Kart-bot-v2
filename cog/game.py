from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ApplicationContext, Role, SlashCommandGroup, option

from .core import Cog

if TYPE_CHECKING:
    from bot import Bot


class GameCog(Cog, name="Game"):

    def __init__(self, bot: Bot) -> None:
        super().__init__(
            bot,
            description="Game related",
            description_localizations={
                "ja": "交流戦関連",
                "en-US": "Game related",
            },
        )

    game = SlashCommandGroup(name="mogi", guild_only=True)

    @game.command(
        name="start",
        description="Start a game",
        description_localizations={
            "ja": "即時集計を開始する",
        },
    )
    @option(
        "enemy",
        type=str,
        name_localizations={
            "ja": "相手チーム",
        },
        description="Enemy team name",
        description_localizations={
            "ja": "相手チームの名前",
        },
        default="A",
    )
    @option(
        "role",
        type=Role,
        name_localizations={
            "ja": "ロール",
        },
        description="Role of participants",
        description_localizations={
            "ja": "参加者メンバーのロール",
        },
        default=None,
    )
    async def game_start(self, ctx: ApplicationContext, enemy: str, role: Role | None) -> None:
        return await self.h.game_start(ctx, enemy, role)


def setup(bot: Bot) -> None:
    bot.add_cog(GameCog(bot))
