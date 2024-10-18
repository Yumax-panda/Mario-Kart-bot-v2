from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

from discord import Embed, File
from discord.ui import Modal as _Modal, View as _View

from utils.constants import EmbedColor
from utils.errors import BotError, get_error_message

__all__ = (
    "View",
    "Modal",
)

if TYPE_CHECKING:
    from discord import Interaction
    from discord.ui.item import Item

    from bot import Bot


class ErrorHandlingMixin:

    async def handle_error(self, error: Exception, *, interaction: Interaction, item: Item | None = None) -> None:
        """エラーが起きたときに呼び出される. `utils.errors.BotError` が発生した場合、エラーのメッセージをチャンネルへ送信する.
        それ以外の場合は、エラーの詳細をファイルに書き込み、Webhookを通じてログチャンネルへ送信する.

        Parameters
        ----------
        error : Exception
            発生したエラー.
        interaction : Interaction
            エラーが発生したInteraction.
        item : Item | None, optional
            Viewの場合, エラーが起きたUIのアイテム, by default None
        """

        if isinstance(error, BotError):
            content: str = error.message.get(interaction.locale, error.message["ja"])  # type: ignore
        else:
            content = "予期しないエラーが発生しました. 時間をおいて再度お試しください."
            error_message = get_error_message(error)

            title = f"Error: {self.__class__.__name__}"

            if item is not None:
                title += f": {item.__class__.__name__}"

            embed = Embed(
                title=title,
                description=f"```py\n{error_message}\n```",
                color=EmbedColor.error,
            )

            if interaction.user is not None:
                embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)

            fp = BytesIO(error_message.encode("utf-8"))
            file = File(fp, "error.txt")

            bot: Bot = interaction.client  # type: ignore
            await bot.h.webhook.send(embed=embed, file=file)

        await interaction.respond(content=content, ephemeral=True)


class View(_View, ErrorHandlingMixin):

    def __init__(
        self,
        *items: Item,
        timeout: float | None = None,
        disable_on_timeout: bool = False,
    ):
        super().__init__(
            *items,
            timeout=timeout,
            disable_on_timeout=disable_on_timeout,
        )

    async def on_error(self, error: Exception, item: Item, interaction: Interaction) -> None:
        await self.handle_error(error, interaction=interaction, item=item)


class Modal(_Modal, ErrorHandlingMixin):
    async def on_error(self, error: Exception, interaction: Interaction) -> None:
        await self.handle_error(error, interaction=interaction)
