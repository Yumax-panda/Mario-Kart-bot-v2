from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ButtonStyle
from discord.ui import Button

from .errors import MessageNotFound

__all__ = ("DeleteButton",)

if TYPE_CHECKING:
    from discord import Interaction


class DeleteButton(Button):

    def __init__(
        self,
        *,
        label: str = "Delete",
        style: ButtonStyle = ButtonStyle.danger,
        disabled: bool = False,
        custom_id: str | None = "delete_button",
    ):
        super().__init__(
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()

        message = interaction.message

        if message is None:
            raise MessageNotFound

        content = message.content
        embeds = message.embeds

        if content or embeds:
            await message.edit(view=None)
        else:
            await message.delete()

        await interaction.respond("終了しました.")
