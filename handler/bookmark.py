from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from discord import ApplicationContext

from ui.bookmark import BookmarkRemoveView, BookmarkView
from utils.constants import MAX_SELECT_OPTIONS

from .errors import BookmarkLimitExceeded, NoBookmarkRegistered, NoPlayerFound
from .types import BaseHandler as IBaseHandler, BookmarkHandler as IBookmarkHandler

__all__ = ("BookmarkHandler",)

if TYPE_CHECKING:
    from discord.ui import View

    from utils.types import HybridContext

    class Options(TypedDict):
        content: str
        view: View

else:
    Options = dict[str, ...]


class BookmarkHandler(IBaseHandler, IBookmarkHandler):
    async def bookmark_stats(self, ctx: HybridContext) -> None:
        if isinstance(ctx, ApplicationContext):
            await ctx.defer()

        bookmark = await self.repo.get_pinned_players(ctx.author.id)  # type: ignore

        if not bookmark:
            raise NoBookmarkRegistered

        view = BookmarkView(bookmark)

        options: Options = {
            "content": "プレイヤーを選択してください.",
            "view": view,
        }

        if isinstance(ctx, ApplicationContext):
            await ctx.respond(**options)
            return

        await ctx.send(**options)

    async def bookmark_add(self, ctx: ApplicationContext, player_name: str, nick: str | None) -> None:
        await ctx.response.defer()
        bookmarks = await self.repo.get_pinned_players(ctx.author.id)

        if len(bookmarks) >= MAX_SELECT_OPTIONS:
            raise BookmarkLimitExceeded

        player = await self.lc.get_player(name=player_name)

        if player is None:
            raise NoPlayerFound

        name = nick or player.name
        await self.repo.put_pinned_player(
            user_id=ctx.author.id,
            player_id=player.id,
            nick_name=name,
        )
        await ctx.respond(f"{name}をブックマークしました.", ephemeral=True)

    async def bookmark_remove(self, ctx: ApplicationContext) -> None:
        await ctx.response.defer()
        bookmarks = await self.repo.get_pinned_players(ctx.author.id)

        if not bookmarks:
            raise NoBookmarkRegistered

        view = BookmarkRemoveView(bookmarks)

        options: Options = {
            "content": "削除するプレイヤーを選択してください.",
            "view": view,
        }

        await ctx.respond(**options)
