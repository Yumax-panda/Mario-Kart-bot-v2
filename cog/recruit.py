from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ApplicationContext, Member, OptionChoice, Role, option, slash_command
from discord.ext import commands

from .core import Cog
from .middlewares import RateLimit, guild_only, is_ignored_channel

if TYPE_CHECKING:
    from bot import Bot
    from utils.types import HybridContext

IGNORE_CHANNEL_IDS = (1066978248711471114, 847026955413225482)


class RecruitCog(Cog, name="Match", command_attrs=dict(guild_only=True)):

    def __init__(self, bot: Bot) -> None:
        super().__init__(
            bot,
            description="Match related",
            description_localizations={
                "ja": "挙手関連",
                "en-US": "Match related",
            },
        )

    r = RateLimit(get_key=lambda c: c.guild.id, max_concurrency=1)

    def cog_check(self, ctx: HybridContext) -> bool:
        # NOTE: テキストコマンドではguild_only属性がないため, ここでバリデーションする必要がある.

        return guild_only(ctx) and not is_ignored_channel(ctx, IGNORE_CHANNEL_IDS)

    @slash_command(
        name="can",
        description="Participate in match",
        description_localizations={"ja": "交流戦へ挙手する"},
    )
    @option(
        name="hours",
        type=str,
        name_localizations={
            "ja": "時間",
        },
        description="Time to participate (multiple available)",
        description_localizations={
            "ja": "参加する時間(複数可)",
        },
    )
    @option(
        "type",
        type=str,
        name_localizations={
            "ja": "タイプ",
        },
        description="Participate, tentative, or substitute",
        description_localizations={
            "ja": "参加, 仮参加, 補欠のいずれか",
        },
        choices=[
            OptionChoice(name="can", name_localizations={"ja": "参加"}, value="c"),
            OptionChoice(name="tentative", name_localizations={"ja": "仮参加"}, value="t"),
            OptionChoice(name="substitute", value="s", name_localizations={"ja": "補欠"}),
        ],
        default="c",
    )
    @option(
        "member",
        type=Member,
        name_localizations={
            "ja": "メンバー",
        },
        description="Member to participate",
        description_localizations={
            "ja": "参加するメンバー",
        },
        default=None,
    )
    @r.limited
    async def can(self, ctx: ApplicationContext, hours: str, type: str, member: Member | None) -> None:
        members = [member or ctx.author]
        handler_map = {
            "c": self.h.can,
            "t": self.h.tentative,
            "s": self.h.substitute,
        }

        return await handler_map[type](ctx, members, hours)

    @commands.command(
        name="can",
        aliases=["c"],
        description="Participate in match",
        brief="交流戦へ挙手する",
        usage="!c [@members] <hours>",
        hidden=False,
    )
    @r.limited
    async def text_can(
        self,
        ctx: commands.Context,
        members: commands.Greedy[Member],
        *,
        hours: str,
    ) -> None:
        return await self.h.can(ctx, members or [ctx.author], hours)

    @commands.command(
        name="tentative",
        aliases=["t"],
        description="Tentative participate in match",
        brief="交流戦へ仮挙手する",
        usage="!t [@members] <hours>",
        hidden=False,
    )
    @r.limited
    async def text_tentative(
        self,
        ctx: commands.Context,
        members: commands.Greedy[Member],
        *,
        hours: str,
    ) -> None:
        return await self.h.tentative(ctx, members or [ctx.author], hours)

    @commands.command(
        name="substitute",
        aliases=["s"],
        description="Substitute in match",
        brief="交流戦の補欠",
        usage="!s [@members] <hours>",
        hidden=False,
    )
    @r.limited
    async def text_substitute(
        self,
        ctx: commands.Context,
        members: commands.Greedy[Member],
        *,
        hours: str,
    ) -> None:
        return await self.h.substitute(ctx, members or [ctx.author], hours)

    @slash_command(
        name="drop",
        description="Cancel participation",
        description_localizations={"ja": "挙手を取り下げる"},
    )
    @option(
        name="hours",
        type=str,
        name_localizations={
            "ja": "時間",
        },
        description="Time to cancel participation",
        description_localizations={
            "ja": "参加を取り下げる時間",
        },
    )
    @option(
        "member",
        type=Member,
        name_localizations={
            "ja": "メンバー",
        },
        description="Member to cancel participation",
        description_localizations={
            "ja": "参加を取り下げるメンバー",
        },
        default=None,
    )
    @r.limited
    async def drop(self, ctx: ApplicationContext, hours: str, member: Member | None) -> None:
        members = [member or ctx.author]
        return await self.h.drop(ctx, members, hours)

    @commands.command(
        name="drop",
        aliases=["d"],
        description="Cancel participation",
        brief="挙手を取り下げる",
        usage="!d [@members] <hours>",
        hidden=False,
    )
    @r.limited
    async def text_drop(
        self,
        ctx: commands.Context,
        members: commands.Greedy[Member],
        *,
        hours: str,
    ) -> None:
        return await self.h.drop(ctx, members or [ctx.author], hours)

    @slash_command(
        name="clear",
        description="Cancel all participation",
        description_localizations={"ja": "挙手を全て取り下げる"},
    )
    @r.limited
    async def clear(self, ctx: ApplicationContext) -> None:
        return await self.h.clear(ctx)

    @commands.command(
        name="clear",
        description="Cancel all participation",
        brief="挙手を全て取り下げる",
        usage="!clear",
        hidden=False,
    )
    @r.limited
    async def text_clear(self, ctx: commands.Context) -> None:
        return await self.h.clear(ctx)

    @slash_command(
        name="out",
        description="Cancel all participation at the specified time",
        description_localizations={"ja": "指定した時間の挙手を全て取り下げる"},
    )
    @option(
        name="hours",
        type=str,
        name_localizations={
            "ja": "時間",
        },
        description="Time to cancel participation",
        description_localizations={
            "ja": "挙手を取り下げる時間",
        },
    )
    @r.limited
    async def out(self, ctx: ApplicationContext, hours: str) -> None:
        return await self.h.out(ctx, hours)

    @commands.command(
        name="out",
        description="Cancel all participation at the specified time",
        brief="指定した時間の挙手を全て取り下げる",
        usage="!out <hours>",
        hidden=False,
    )
    @r.limited
    async def text_out(self, ctx: commands.Context, hours: str) -> None:
        return await self.h.out(ctx, hours)

    @slash_command(
        name="now",
        description="Show current participation status",
        description_localizations={"ja": "現在の挙手状況を表示する"},
    )
    @r.limited
    async def now(self, ctx: ApplicationContext) -> None:
        return await self.h.now(ctx)

    @commands.command(
        name="now",
        description="Show current participation status",
        aliases=["warlist", "list"],
        brief="現在の挙手状況を表示する",
        usage="!now",
        hidden=False,
    )
    @r.limited
    async def text_now(self, ctx: commands.Context) -> None:
        return await self.h.now(ctx)

    @slash_command(
        name="pick",
        description="Randomly pick a member",
        description_localizations={"ja": "メンバーをランダムに選ぶ"},
    )
    @option(
        name="role",
        type=Role,
        name_localizations={
            "ja": "ロール",
        },
        description="Members' role",
        description_localizations={
            "ja": "メンバーのロール",
        },
    )
    async def pick(self, ctx: ApplicationContext, role: Role) -> None:
        return await self.h.pick(ctx, role)

    @commands.command(
        name="pick",
        description="Randomly pick a member",
        brief="メンバーをランダムに選ぶ",
        usage="!pick <role>",
        hidden=False,
    )
    async def text_pick(self, ctx: commands.Context, role: Role) -> None:
        return await self.h.pick(ctx, role)


def setup(bot: Bot) -> None:
    bot.add_cog(RecruitCog(bot))
