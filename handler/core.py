from __future__ import annotations

import asyncio
import logging
from functools import cached_property
from typing import TYPE_CHECKING

from discord import Webhook

from .types import BaseHandler as IBaseHandler

if TYPE_CHECKING:
    from mk8dx.lounge.player import Player
    from utils.constants import Season


__all__ = ("BaseHandler",)


class BaseHandler(IBaseHandler):

    async def get_players_by_user_ids(
        self,
        user_ids: list[int],
        season: Season | None = None,
    ) -> list[tuple[int, Player | None]]:

        async def get_player(user_id: int) -> tuple[int, Player | None]:
            lounge_id = await self.repo.get_lounge_id(user_id)
            linked_id = lounge_id or user_id
            player = await self.lc.get_player(discord_id=linked_id, season=season)
            if player is not None:
                player.link_id(user_id)
            return user_id, player

        return await asyncio.gather(*[get_player(user_id) for user_id in user_ids])

    async def get_players_by_friend_codes(
        self,
        friend_codes: list[str],
        season: Season | None = None,
    ) -> list[tuple[str, Player | None]]:

        async def get_player(friend_code: str) -> tuple[str, Player | None]:
            player = await self.lc.get_player(fc=friend_code, season=season)
            return friend_code, player

        return await asyncio.gather(*[get_player(friend_code) for friend_code in friend_codes])

    @cached_property
    def webhook(self) -> Webhook:
        return Webhook.from_url(self._webhook_token, session=self.session)

    async def setup_repository(self) -> None:
        repo = await self.config.get_repository()
        self.repo = repo
        logging.info("Repository setup completed.")
