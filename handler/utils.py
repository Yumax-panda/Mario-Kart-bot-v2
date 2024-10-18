from __future__ import annotations

from typing import TYPE_CHECKING, Any

from discord import Color, Embed
from discord.ext import commands
from discord.ext.pages import Paginator

from utils.constants import EmbedColor

__all__ = ("SimplifiedPaginator", "EmbedPaginator")

if TYPE_CHECKING:
    from datetime import datetime

    from discord.embeds import EmbedAuthor, EmbedFooter, EmbedMedia, EmbedType
    from discord.ext.pages import Page, PageGroup, PaginatorButton
    from discord.ui import View


class SimplifiedPaginator(Paginator):
    """1ページしかページが存在しない場合にコンパクトな表示を行うPaginator.
    使い方は`discord.ext.pages.Paginator`と同じ.
    """

    def __init__(
        self,
        pages: list[PageGroup] | list[Page] | list[str] | list[list[Embed] | Embed],
        show_menu=False,
        menu_placeholder: str = "Select Page Group",
        author_check=False,
        disable_on_timeout=True,
        use_default_buttons=True,
        default_button_row: int = 0,
        loop_pages: bool = False,
        custom_view: View | None = None,
        timeout: float | None = 180,
        custom_buttons: list[PaginatorButton] | None = None,
        trigger_on_display: bool | None = None,
    ) -> None:
        is_compact = len(pages) <= 1
        super().__init__(
            pages,
            show_disabled=not is_compact,
            show_indicator=not is_compact,
            show_menu=show_menu,
            menu_placeholder=menu_placeholder,
            author_check=author_check,
            disable_on_timeout=disable_on_timeout,
            use_default_buttons=use_default_buttons,
            default_button_row=default_button_row,
            loop_pages=loop_pages,
            custom_view=custom_view,
            timeout=timeout,
            custom_buttons=custom_buttons,
            trigger_on_display=trigger_on_display,
        )


class EmbedPaginator(commands.Paginator):

    def __init__(self, prefix: str = "", suffix: str = "") -> None:
        super().__init__(
            prefix=prefix,
            suffix=suffix,
        )

    def to_embeds(
        self,
        header: str | None = None,
        footer: str | None = None,
        color: int | Color | None = None,
        title: str | None = None,
        type: EmbedType = "rich",
        url: Any | None = None,
        timestamp: datetime | None = None,
        author: EmbedAuthor | None = None,
        embed_footer: EmbedFooter | None = None,
        image: str | EmbedMedia | None = None,
        thumbnail: str | EmbedMedia | None = None,
    ) -> list[Embed]:
        """内容をEmbedに変換する.

        Returns
        -------
        list[Embed]
            Embedのリスト
        """
        embeds: list[Embed] = []
        color = color or EmbedColor.default

        for page in self.pages:
            description = "\n".join(filter(None, [header, page, footer]))
            embed = Embed(
                color=color,
                title=title,
                type=type,
                url=url,
                description=description,
                timestamp=timestamp,
                author=author,
                footer=embed_footer,
                image=image,
                thumbnail=thumbnail,
            )
            embeds.append(embed)
        return embeds
