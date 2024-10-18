from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Mapping, TypedDict

from discord import ApplicationContext, Embed, SlashCommand
from discord.ext import commands
from typing_extensions import Required

from utils.constants import EmbedColor

from .errors import NoPlayerFound
from .types import BaseHandler as IBaseHandler, UtilityHandler as IUtilityHandler
from .utils import SimplifiedPaginator

__all__ = ("UtilityHandler",)

if TYPE_CHECKING:
    from bot import Bot
    from cog.core import Cog
    from utils.constants import Locale, LocaleDict
    from utils.types import HybridContext

    Attr = Literal["mmr", "max_mmr"]

    class Options(TypedDict, total=False):
        embed: Required[Embed]
        content: str


class UtilityHandler(IBaseHandler, IUtilityHandler):
    async def help(self, ctx: ApplicationContext, locale: Locale | None = None) -> None:
        await ctx.response.defer(ephemeral=True)

        lang: Locale = locale or "ja"

        embeds: list[Embed] = []

        attentions: LocaleDict = {
            "ja": (
                ":warning: __**注意**__\n戦績データの管理は本botで行っていますが、万が一データが消失した場合でも**一切の責任は負いません**。"
                "定期的に各自で**データのバックアップを取ることを強く推奨**します。"
                "戦績データのファイルを出力するには`/result data export`、botへファイルを読み込むには`/result data load`で行えます。"
            ),
            "en-US": (
                ":warning: __**Attention**__\nThis bot manages your result data, but **we are not responsible for any data loss**."
                "**We strongly recommend that you back up your data regularly.**"
                "To export your result data, use `/result data export`, and to import it, use `/result data load`."
            ),
        }

        footers: LocaleDict = {
            "ja": "<必須> [任意]",
            "en-US": "<Required> [Optional]",
        }

        bot: Bot = ctx.bot  # type: ignore
        cogs: Mapping[str, Cog] = bot.cogs  # type: ignore

        for name, cog in cogs.items():
            if cog.hidden:
                continue

            title: str = cog.description_localizations.get(lang, cog.description)
            embed = Embed(title=title, color=EmbedColor.default)

            if name == "Result":
                embed.description = attentions[lang]

            embed.set_footer(text=footers[lang])

            for command in cog.walk_commands():
                if isinstance(command, SlashCommand):
                    usage = command.description_localizations.get(lang, command.description)
                    embed.add_field(
                        name=f"/{command.qualified_name}",
                        value=f"> {usage}",
                        inline=False,
                    )
                elif isinstance(command, commands.Command):
                    if command.hidden:
                        continue

                    usage = command.brief if lang == "ja" else command.description

                    embed.add_field(
                        name=command.usage,
                        value=f"> {usage}",
                        inline=False,
                    )

            embeds.append(embed)
        owner = bot.get_user(ctx.bot.owner_id)

        if owner:
            contact_embed = Embed(title="Contact", color=EmbedColor.default)
            contact_embed.set_author(name=str(owner), icon_url=owner.display_avatar.url)
            embeds.append(contact_embed)

        paginator = SimplifiedPaginator(pages=embeds)  # type: ignore
        await paginator.respond(ctx.interaction, ephemeral=True)

    async def link(self, ctx: HybridContext, name: str) -> None:
        player = await self.lc.get_player(name=name)

        if player is None or player.discord_id is None:
            raise NoPlayerFound

        user_id = str(ctx.author.id)

        await self.repo.put_lounge_id(user_id=int(user_id), lounge_id=int(player.discord_id))

        if isinstance(ctx, commands.Context):
            await ctx.send(f"{player.name}を連携しました.")
            return

        await ctx.respond({"ja": f"{player.name}と連携しました."}.get(ctx.locale, f"Linked to {player.name}."))
