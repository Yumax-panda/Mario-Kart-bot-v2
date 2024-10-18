from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ApplicationContext, SlashCommandGroup, option

from .core import Cog

if TYPE_CHECKING:
    from bot import Bot


class BookmarkCog(Cog, name="Bookmark"):

    def __init__(self, bot: Bot) -> None:
        super().__init__(
            bot,
            description="Bookmark",
            description_localizations={
                "ja": "ブックマーク",
                "en-US": "Bookmark",
            },
        )

    bookmark = SlashCommandGroup(name="bookmark", description="Bookmark")

    @bookmark.command(
        name="stats",
        description="Show bookmarked player's stats",
        description_localizations={"ja": "お気に入りのプレイヤーのstatsを表示"},
    )
    async def bookmark_stats(self, ctx: ApplicationContext) -> None:
        return await self.h.bookmark_stats(ctx)

    # TODO: フレンドコードやdiscord_idでも検索できるようにする
    @bookmark.command(
        name="add",
        description="Add a player to bookmark",
        description_localizations={"ja": "プレイヤーをお気に入りに追加"},
    )
    @option(
        name="name",
        type=str,
        parameter_name="player_name",
        name_localizations={"ja": "プレイヤー名"},
        description="Player name",
        description_localizations={"ja": "登録するプレイヤーのラウンジ名"},
    )
    @option(
        name="nick",
        type=str,
        parameter_name="nick",
        name_localizations={"ja": "ニックネーム"},
        description="Nickname",
        description_localizations={"ja": "プレイヤーのニックネーム"},
        default=None,
        required=False,
    )
    async def bookmark_add(self, ctx: ApplicationContext, player_name: str, nick: str | None) -> None:
        return await self.h.bookmark_add(ctx, player_name, nick)

    @bookmark.command(
        name="remove",
        description="Remove a player from bookmark",
        description_localizations={"ja": "プレイヤーをお気に入りから削除"},
    )
    async def bookmark_remove(self, ctx: ApplicationContext) -> None:
        return await self.h.bookmark_remove(ctx)


def setup(bot: Bot) -> None:
    bot.add_cog(BookmarkCog(bot))
