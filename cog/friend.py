from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ApplicationContext, OptionChoice, SlashCommandGroup, option
from discord.ext import commands
from discord.ext.commands import BucketType, MaxConcurrency

from .core import Cog

if TYPE_CHECKING:
    from bot import Bot


class FriendCog(Cog, name="Friend"):
    def __init__(self, bot: Bot) -> None:
        super().__init__(
            bot,
            description="Friend related",
            description_localizations={
                "ja": "フレンド関連",
                "en-US": "Friend related",
            },
        )

    friend = SlashCommandGroup(
        name="friend",
        max_concurrency=MaxConcurrency(1, per=BucketType.user, wait=False),
    )

    @friend.command(
        name="mmr",
        description="Search MMRs by friend codes.",
        description_localizations={"ja": "フレンドコードでMMRを一括検索"},
    )
    @option(
        type=str,
        parameter_name="text",
        name="friend_codes",
        name_localizations={"ja": "フレンドコード"},
        description="0000-0000-0000 format will be detected.",
        description_localizations={"ja": "フレンドコードが含まれる文章を入力してください。(0000-0000-0000形式)"},
        required=True,
    )
    @option(
        type=str,
        parameter_name="ascending",
        name="order",
        name_localizations={"ja": "順序"},
        description="Sort according to MMR",
        description_localizations={"ja": "MMRで並び替え"},
        choices=[
            OptionChoice(
                name="ascending",
                name_localizations={"ja": "低い順"},
                value="ascending",
            ),
            OptionChoice(
                name="descending",
                name_localizations={"ja": "高い順"},
                value="descending",
            ),
            OptionChoice(name="default", name_localizations={"ja": "そのまま"}, value=""),
        ],
        required=False,
        default="",
    )
    @option(
        type=str,
        parameter_name="view_original",
        name="view_original",
        name_localizations={"ja": "入力テキスト"},
        description="Whether or not display original text.",
        description_localizations={"ja": "入力されたテキストを表示するかどうか"},
        required=False,
        default="...",
        choices=[
            OptionChoice(name="Yes", name_localizations={"ja": "表示"}, value="..."),
            OptionChoice(name="No", name_localizations={"ja": "非表示"}, value=""),
        ],
    )
    async def friend_mmr(self, ctx: ApplicationContext, text: str, ascending: str, view_original: str) -> None:
        asc = {
            "ascending": True,
            "descending": False,
            "": None,
        }
        return await self.h.friend_mmr(ctx, text=text, ascending=asc[ascending], view_original=bool(view_original))

    @commands.command(
        name="fm",
        description="Search MMRs by friend codes.",
        brief="フレンドコードでMMRを検索",
        usage="!fm <switch friend codes>",
        hidden=False,
    )
    async def text_friend_mmr(self, ctx: commands.Context, *, text: str) -> None:
        await self.h.friend_mmr(ctx, text=text, ascending=None)

    @commands.command(
        name="fmh",
        aliases=["fh"],
        description="Search MMRs by friend codes. (dec)",
        brief="フレンドコードでMMRを検索(高い順)",
        usage="!fmh <switch friend codes>",
        hidden=False,
    )
    async def text_friend_mmr_high(self, ctx: commands.Context, *, text: str) -> None:
        await self.h.friend_mmr(ctx, text=text, ascending=False)

    @commands.command(
        name="fml",
        aliases=["fl"],
        description="Search MMRs by friend codes. (asc)",
        brief="フレンドコードでMMRを検索(低い順)",
        usage="!fml <switch friend codes>",
        hidden=False,
    )
    async def text_friend_mmr_low(self, ctx: commands.Context, *, text: str) -> None:
        await self.h.friend_mmr(ctx, text=text, ascending=True)

    @friend.command(
        name="peak_mmr",
        description="Search Peak MMRs by friend codes.",
        description_localizations={"ja": "フレンドコードでPeak MMRを一括検索"},
    )
    @option(
        type=str,
        parameter_name="text",
        name="friend_codes",
        name_localizations={"ja": "フレンドコード"},
        description="0000-0000-0000 format will be detected.",
        description_localizations={"ja": "フレンドコードが含まれる文章を入力してください。(0000-0000-0000形式)"},
        required=True,
    )
    @option(
        type=str,
        parameter_name="ascending",
        name="order",
        name_localizations={"ja": "順序"},
        description="Sort according to MMR",
        description_localizations={"ja": "MMRで並び替え"},
        choices=[
            OptionChoice(
                name="ascending",
                name_localizations={"ja": "低い順"},
                value="ascending",
            ),
            OptionChoice(
                name="descending",
                name_localizations={"ja": "高い順"},
                value="descending",
            ),
            OptionChoice(name="default", name_localizations={"ja": "そのまま"}, value=""),
        ],
        required=False,
        default="",
    )
    @option(
        type=str,
        parameter_name="view_original",
        name="view_original",
        name_localizations={"ja": "入力テキスト"},
        description="Whether or not display original text.",
        description_localizations={"ja": "入力されたテキストを表示するかどうか"},
        required=False,
        default="...",
        choices=[
            OptionChoice(name="Yes", name_localizations={"ja": "表示"}, value="..."),
            OptionChoice(name="No", name_localizations={"ja": "非表示"}, value=""),
        ],
    )
    async def friend_peak_mmr(self, ctx: ApplicationContext, text: str, ascending: str, view_original: str) -> None:
        asc = {
            "ascending": True,
            "descending": False,
            "": None,
        }
        return await self.h.friend_peak_mmr(ctx, text=text, ascending=asc[ascending], view_original=bool(view_original))

    @commands.command(
        name="peak",
        description="Search Peak MMRs by friend codes.",
        brief="フレンドコードでPeak MMRを検索",
        usage="!peak <switch friend codes>",
        hidden=False,
    )
    async def text_friend_peak_mmr(self, ctx: commands.Context, *, text: str) -> None:
        await self.h.friend_peak_mmr(ctx, text=text, ascending=None)

    @commands.command(
        name="peakh",
        aliases=["ph"],
        description="Search Peak MMRs by friend codes. (dec)",
        brief="フレンドコードでPeak MMRを検索(高い順)",
        usage="!peakh <switch friend codes>",
        hidden=False,
    )
    async def text_friend_peak_mmr_high(self, ctx: commands.Context, *, text: str) -> None:
        await self.h.friend_peak_mmr(ctx, text=text, ascending=False)

    @commands.command(
        name="peakl",
        aliases=["pl"],
        description="Search Peak MMRs by friend codes. (asc)",
        brief="フレンドコードでPeak MMRを検索(低い順)",
        usage="!peakl <switch friend codes>",
        hidden=False,
    )
    async def text_friend_peak_mmr_low(self, ctx: commands.Context, *, text: str) -> None:
        await self.h.friend_peak_mmr(ctx, text=text, ascending=True)


def setup(bot: Bot) -> None:
    bot.add_cog(FriendCog(bot))
