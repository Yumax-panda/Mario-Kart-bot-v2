from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ApplicationContext, Role, SlashCommandGroup, option

from utils.constants import CURRENT_SEASON, MIN_SEASON

from .core import Cog

if TYPE_CHECKING:
    from bot import Bot
    from utils.constants import Season


class TeamCog(Cog, name="Team"):
    def __init__(self, bot: Bot) -> None:
        super().__init__(
            bot,
            description="Manage team info",
            description_localizations={
                "ja": "チーム関連",
                "en-US": "Manage team info",
            },
        )

    team = SlashCommandGroup(name="team", guild_only=True)

    @team.command(
        name="mmr",
        description="Average MMR",
        description_localizations={"ja": "チームの平均MMRを計算"},
    )
    @option(
        "role",
        type=Role,
        name_localizations={"ja": "ロール"},
        description="Role to calculate average MMR",
        description_localizations={"ja": "平均MMRを計算するロール"},
        required=True,
    )
    @option(
        "season",
        type=int,
        name_localizations={"ja": "シーズン"},
        description="Season",
        description_localizations={"ja": "シーズン"},
        min_value=MIN_SEASON,
        max_value=CURRENT_SEASON,
        required=False,
    )
    async def mmr(self, ctx: ApplicationContext, role: Role, season: Season | None = None) -> None:
        return await self.h.team_mmr(ctx, role, season)

    @team.command(
        name="peak_mmr",
        description="Average Peak MMR",
        description_localizations={"ja": "チームの平均Peak MMRを計算"},
    )
    @option(
        "role",
        type=Role,
        name_localizations={"ja": "ロール"},
        description="Role to calculate average peak MMR",
        description_localizations={"ja": "平均Peak MMRを計算するロール"},
        required=True,
    )
    @option(
        "season",
        type=int,
        name_localizations={"ja": "シーズン"},
        description="Season",
        description_localizations={"ja": "シーズン"},
        min_value=MIN_SEASON,
        max_value=CURRENT_SEASON,
        required=False,
    )
    async def team_peak_mmr(self, ctx: ApplicationContext, role: Role, season: Season | None = None) -> None:
        return await self.h.team_peak_mmr(ctx, role, season)

    @team.command(
        name="mkc",
        description="Show MKC web urls",
        description_localizations={"ja": "MKCのWebページを表示"},
    )
    @option(
        "role",
        type=Role,
        name_localizations={"ja": "ロール"},
        description="Role to show MKC web urls",
        description_localizations={"ja": "MKCのWebページを表示するロール"},
        required=True,
    )
    async def team_mkc(self, ctx: ApplicationContext, role: Role) -> None:
        return await self.h.team_mkc(ctx, role)

    name = team.create_subgroup(name="name")

    @name.command(
        name="set",
        description="Set team name",
        description_localizations={"ja": "チーム名を設定"},
    )
    @option(
        "name",
        type=str,
        name_localizations={"ja": "チーム名"},
        description="Team name",
        description_localizations={"ja": "チーム名"},
        required=True,
    )
    async def team_name_set(self, ctx: ApplicationContext, name: str) -> None:
        return await self.h.team_name_set(ctx, name)

    @name.command(
        name="show",
        description="Show team name",
        description_localizations={"ja": "チーム名を表示"},
    )
    async def team_name_show(self, ctx: ApplicationContext) -> None:
        return await self.h.team_name_show(ctx)


def setup(bot: Bot) -> None:
    bot.add_cog(TeamCog(bot))
