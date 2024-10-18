from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ApplicationContext, Role

from mk8dx.lounge.rank import Rank
from utils.utils import drop_duplicates, get_average

from .errors import GuildNotFound, NoViewablePlayers, TeamNameNotSet
from .types import BaseHandler as IBaseHandler, TeamHandler as ITeamHandler
from .utils import EmbedPaginator, SimplifiedPaginator

__all__ = ("TeamHandler",)

if TYPE_CHECKING:
    from discord import ApplicationContext, Embed, Role

    from mk8dx.lounge.player import Player
    from utils.constants import Season


class TeamHandler(IBaseHandler, ITeamHandler):
    async def team_mmr(self, ctx: ApplicationContext, role: Role, season: Season | None = None) -> None:
        await ctx.response.defer()
        players_with_key = await self.get_players_by_user_ids(
            user_ids=[member.id for member in role.members],
            season=season,
        )
        dropped = drop_duplicates([(getattr(p, "name", "..."), p) for _, p in players_with_key])

        sorted_players = sorted(
            [p for _, p in dropped],
            key=lambda player: getattr(player, "mmr", 0) or 0,
            reverse=True,
        )

        avg = get_average(sorted_players, lambda p: getattr(p, "mmr", None))

        if avg is None:
            raise NoViewablePlayers

        page = EmbedPaginator()

        for idx, p in enumerate(sorted_players):
            if p is None or p.mmr is None:
                continue
            page.add_line(f"{str(idx + 1).rjust(3)}: [{p.name}]({p.lounge_url}) ({int(p.mmr)})")

        title = f"Average MMR: {avg:.1f}" if season is None else f"Average MMR (S{season}): {avg:.1f}"
        header = f"**Role** {role.mention}"
        rank = Rank.from_mmr(mmr=avg, season=season)

        embeds = page.to_embeds(
            title=title,
            header=header,
            footer=f"Rank: {rank.name}",
            color=rank.color,
            thumbnail=rank.url,
        )

        await SimplifiedPaginator(embeds).respond(ctx.interaction)  # type: ignore # List[Embed] is in List[list[Embed] | Embed]

    async def team_peak_mmr(
        self,
        ctx: ApplicationContext,
        role: Role,
        season: Season | None = None,
    ) -> None:
        await ctx.response.defer()
        players_with_key = await self.get_players_by_user_ids(
            user_ids=[member.id for member in role.members],
            season=season,
        )
        dropped = drop_duplicates([(getattr(p, "name", "..."), p) for _, p in players_with_key])

        sorted_players = sorted(
            [p for _, p in dropped],
            key=lambda player: getattr(player, "max_mmr", 0) or 0,
            reverse=True,
        )

        avg = get_average(sorted_players, lambda p: getattr(p, "max_mmr", None))

        if avg is None:
            raise NoViewablePlayers

        page = EmbedPaginator()

        for idx, p in enumerate(sorted_players):
            if p is None or p.max_mmr is None:
                continue
            page.add_line(f"{str(idx + 1).rjust(3)}: [{p.name}]({p.lounge_url}) ({int(p.max_mmr)})")

        title = f"Average Peak MMR: {avg:.1f}" if season is None else f"Average Peak MMR (S{season}): {avg:.1f}"
        header = f"**Role** {role.mention}"
        rank = Rank.from_mmr(mmr=avg, season=season)

        embeds = page.to_embeds(
            title=title,
            header=header,
            footer=f"Rank: {rank.name}",
            color=rank.color,
            thumbnail=rank.url,
        )

        await SimplifiedPaginator(embeds).respond(ctx.interaction)  # type: ignore # List[Embed] is in List[list[Embed] | Embed]

    async def team_mkc(
        self,
        ctx: ApplicationContext,
        role: Role,
    ) -> None:
        await ctx.response.defer()
        players_with_key = await self.get_players_by_user_ids(user_ids=[member.id for member in role.members])
        dropped = drop_duplicates([(p.linked_id or "...", p) for _, p in players_with_key if p is not None])
        players = [p for _, p in dropped]

        if not players:
            raise NoViewablePlayers

        embeds = create_mkc_embeds(players=players, role=role)
        await SimplifiedPaginator(embeds).respond(ctx.interaction)  # type: ignore # List[Embed] is in List[list[Embed] | Embed]

    async def team_name_set(self, ctx: ApplicationContext, name: str) -> None:
        await ctx.response.defer()
        if ctx.guild_id is None:
            raise GuildNotFound
        await self.repo.put_team_name(ctx.guild_id, name)
        await ctx.respond({"ja": f"チーム名を登録しました  **{name}**"}.get(ctx.locale, f"Set team name **{name}**"))

    async def team_name_show(self, ctx: ApplicationContext) -> None:
        await ctx.response.defer()
        if ctx.guild_id is None:
            raise GuildNotFound
        name = await self.repo.get_team_name(ctx.guild_id)
        if name is None:
            raise TeamNameNotSet
        await ctx.respond(f"**{name}**")


def create_mkc_embeds(players: list[Player], role: Role) -> list[Embed]:
    page = EmbedPaginator()
    for idx, p in enumerate(players):
        page.add_line(f"{str(idx + 1).rjust(3)}: [{p.name}]({p.mkc_url}) {f'({p.switch_fc})' if p.switch_fc else ''}")

    return page.to_embeds(title="MKC Registry", header=f"**Role** {role.mention}", footer=f"Total: {len(players)} players")
