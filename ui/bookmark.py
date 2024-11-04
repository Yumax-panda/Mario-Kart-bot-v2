from __future__ import annotations

from typing import TYPE_CHECKING

from discord import SelectOption
from discord.ui import string_select

from model.pinned_players import PinnedPlayer
from utils.constants import CURRENT_SEASON, MAX_SELECT_OPTIONS, MIN_SEASON

from .core import View
from .errors import FailedToGetUserData, InvalidMessage, MessageNotFound, PlayerNotFound, PlayerNotSelected
from .utils import DeleteButton

__all__ = (
    "BookmarkView",
    "BookmarkRemoveView",
)

if TYPE_CHECKING:
    from discord import Interaction
    from discord.ui import Select

    from bot import Bot


# TODO: interaction_checkで自分のブックマークのみ編集できるようにする


class BookmarkView(View):

    def __init__(self, players: list[PinnedPlayer] = []) -> None:
        """ブックマークされたプレイヤーのStatsを表示するView.
        コマンドで呼び出してこのViewを表示する際は, playersが空でないことを保証すること.

        Parameters
        ----------
        players : list[PinnedPlayer], optional
            ブックマークされたプレイヤーのリスト, by default [].
        """
        super().__init__()

        options: list[SelectOption] = []

        for player in players[:MAX_SELECT_OPTIONS]:
            options.append(SelectOption(label=player.nick_name, value=player.repr))

        self.change_player.options = options  # type: ignore

        self.add_item(DeleteButton(label="終了", custom_id="stats_exit"))

    @string_select(placeholder="Player", custom_id="stats_player")
    async def change_player(self, select: Select, interaction: Interaction) -> None:
        """ブックマークしたプレイヤーを選択して表示されているStatsを変更する.

        Parameters
        ----------
        select : Select
            付属されているSelect.
        interaction : Interaction
            送信されたInteraction.
        """
        await interaction.response.defer()

        value: str = select.values[0]  # type: ignore
        player = PinnedPlayer.from_repr(value)

        bot: Bot = interaction.client  # type: ignore

        details = await bot.h.lc.get_player_details(player_id=player.id, season=CURRENT_SEASON)  # type: ignore

        if details is None:
            raise PlayerNotFound

        options = details.to_stats(display_name=player.nick_name)
        message = interaction.message

        if message is None:
            raise MessageNotFound

        await message.edit(**options)
        await interaction.respond("プレイヤーを選択しました.", ephemeral=True)

    @string_select(
        placeholder="Season",
        options=[SelectOption(label=str(season), value=str(season)) for season in range(MIN_SEASON, CURRENT_SEASON + 1)],
        custom_id="stats_season",
    )
    async def change_season(self, select: Select, interaction: Interaction) -> None:
        """表示されているStatsのSeasonを変更する.

        Parameters
        ----------
        select : Select
            付属されているSelect.
        interaction : Interaction
            送信されたInteraction.
        """
        await interaction.response.defer()

        message = interaction.message

        if message is None:
            raise MessageNotFound

        embeds = message.embeds

        if not embeds:
            raise PlayerNotSelected

        embed = embeds[0].copy()
        title = embed.title
        description = embed.description

        if not isinstance(title, str) or not isinstance(description, str):
            raise InvalidMessage

        display_name = title.split("'s stats", maxsplit=1)[0]
        player_id = description.split("PlayerDetails/", maxsplit=1)[1].split("?")[0].replace(")", "")

        season = int(select.values[0])  # type: ignore
        bot: Bot = interaction.client  # type: ignore

        details = await bot.h.lc.get_player_details(player_id=player_id, season=season)  # type: ignore

        if details is None:
            raise PlayerNotFound

        options = details.to_stats(display_name=display_name)
        await message.edit(**options)
        await interaction.respond(f"シーズン{season}へ変更しました.", ephemeral=True)


class BookmarkRemoveView(View):

    def __init__(self, players: list[PinnedPlayer] = []) -> None:
        """ブックマークされたプレイヤーを削除するView.

        Parameters
        ----------
        players : list[PinnedPlayer], optional
            ブックマークされたプレイヤーのリスト, by default [].
        """
        super().__init__(timeout=180.0, disable_on_timeout=True)

        options: list[SelectOption] = []

        for player in players[:MAX_SELECT_OPTIONS]:
            options.append(SelectOption(label=player.nick_name, value=player.repr))

        self.remove_player.options = options  # type: ignore

    @string_select(
        placeholder="お気に入り削除するプレイヤーを選択してください",
        custom_id="bookmark_remove",
    )
    async def remove_player(self, select: Select, interaction: Interaction) -> None:
        """ブックマークされたプレイヤーを選択して削除する.

        Parameters
        ----------
        select : Select
            付属されているSelect.
        interaction : Interaction
            送信されたInteraction.
        """
        await interaction.response.defer()

        value: str = select.values[0]  # type: ignore
        player = PinnedPlayer.from_repr(value)

        bot: Bot = interaction.client  # type: ignore

        if (user := interaction.user) is None:
            raise FailedToGetUserData

        await bot.h.repo.delete_pinned_player(
            user_id=user.id,
            player_id=int(player.id),
        )

        deleted_name = player.nick_name

        await interaction.respond(f"{deleted_name}を削除しました.", ephemeral=True)
