from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar, Final, Literal, TypeVar

from aiohttp import ClientSession

from utils.constants import CURRENT_SEASON

from .leaderboard import LeaderBoard
from .player import Player, PlayerDetails
from .types.client import LoungeClient as ILoungeClient, SortBy
from .utils import BaseModel, Search

__all__ = ("LoungeClient",)

GetPlayerParams = Literal["id", "name", "mkcId", "discordId", "fc"]
GetPlayerDetailsParams = Literal["id", "name"]

T = TypeVar("T", bound=BaseModel)

if TYPE_CHECKING:
    from utils.constants import Season

logger = logging.getLogger(__name__)


class LoungeClient(ILoungeClient):
    GET_PLAYER_PARAMS: ClassVar[tuple[GetPlayerParams, ...]] = (
        "id",
        "name",
        "mkcId",
        "discordId",
        "fc",
    )
    GET_PLAYER_DETAILS_PARAMS: ClassVar[tuple[GetPlayerDetailsParams, ...]] = (
        "id",
        "name",
    )
    API_URL: Final[str] = "https://www.mk8dx-lounge.com/api/"

    if TYPE_CHECKING:
        _players_cache: dict[GetPlayerParams, dict[str, Player | None]]
        _player_details_cache: dict[GetPlayerDetailsParams, dict[str, PlayerDetails | None]]

    def __init__(self) -> None:
        self._clear_cache()

    def _clear_cache(self) -> None:
        self._players_cache = {query: {} for query in self.GET_PLAYER_PARAMS}
        self._player_details_cache = {query: {} for query in self.GET_PLAYER_DETAILS_PARAMS}

    async def __get(self, path: str, params: dict, cls: type[T]) -> T | None:
        async with ClientSession() as session:
            async with session.get(f"{self.API_URL}{path}", params=params) as response:
                if response.status != 200:
                    return None
                return cls(await response.json())

    async def get_player(
        self,
        player_id: int | str | None = None,
        name: str | None = None,
        mkc_id: int | str | None = None,
        discord_id: int | str | None = None,
        fc: str | None = None,
        season: Season | None = None,
    ) -> Player | None:
        # NOTE: 本当はseasonを指定せずにリクエストをしても最新のシーズンの情報が返ってくるが,
        # 以下の理由でseasonを明示的に指定するようにしている. (他のメソッドも同様)
        #
        # - キャッシュのキーにseasonを含めることで, シーズンごとにキャッシュを分けることができる.
        # - season: Noneのようにseason未定義時のキャッシュキーを対応させると, API側でシーズンがbotのライフサイクル内で変更された場合にキャッシュが使い回されてしまう.

        params: dict[GetPlayerParams | Literal["season"], str] = {
            "season": str(season) if season is not None else str(CURRENT_SEASON)
        }
        query: GetPlayerParams | None = None

        if player_id is not None:
            params["id"] = str(player_id)
            query = "id"
        elif mkc_id is not None:
            params["mkcId"] = str(mkc_id)
            query = "mkcId"
        elif discord_id is not None:
            params["discordId"] = str(discord_id)
            query = "discordId"
        elif name is not None:
            params["name"] = str(name)
            query = "name"
        elif fc is not None:
            params["fc"] = fc
            query = "fc"
        else:
            return None

        identifier = f"{params[query]}-season:{params['season']}"
        try:
            return self._players_cache[query][identifier]
        except KeyError:
            logger.debug(f"Player query:{query}, id:{identifier} not found in cache")
            player = await self.__get("player", params, Player)
            self._players_cache[query][identifier] = player

            return player

    async def get_player_details(
        self,
        player_id: int | str | None = None,
        name: str | None = None,
        season: Season | None = None,
    ) -> PlayerDetails | None:
        params: dict[GetPlayerDetailsParams | Literal["season"], str] = {
            "season": str(season) if season is not None else str(CURRENT_SEASON)
        }
        query: GetPlayerDetailsParams | None = None

        if player_id is not None:
            params["id"] = str(player_id)
            query = "id"
        elif name is not None:
            params["name"] = str(name)
            query = "name"
        else:
            return None

        identifier = f"{params[query]}-season:{params['season']}"

        try:
            return self._player_details_cache[query][identifier]
        except KeyError:
            logger.debug(f"PlayerDetails query:{query}, id:{identifier} not found in cache")
            player = await self.__get("player/details", params, PlayerDetails)
            self._player_details_cache[query][identifier] = player

            return player

    async def get_leaderboard(
        self,
        season: Season | None = None,
        skip: int = 0,
        page_size: int = 50,
        search: Search | None = None,
        sort_by: SortBy | None = None,
        country: str | None = None,
        min_mmr: int | None = None,
        max_mmr: int | None = None,
        min_events_played: int | None = None,
        max_events_played: int | None = None,
    ) -> LeaderBoard:
        params = {
            "season": str(season) if season is not None else str(CURRENT_SEASON),
            "skip": str(skip),
            "pageSize": str(page_size),
        }
        if search is not None:
            params["search"] = search.query
        if sort_by is not None:
            params["sortBy"] = sort_by
        if country is not None:
            params["country"] = country
        if min_mmr is not None:
            params["minMmr"] = str(min_mmr)
        if max_mmr is not None:
            params["maxMmr"] = str(max_mmr)
        if min_events_played is not None:
            params["minEventsPlayed"] = str(min_events_played)
        if max_events_played is not None:
            params["maxEventsPlayed"] = str(max_events_played)

        data = await self.__get("leaderboard", params, LeaderBoard)

        if data is None:
            return LeaderBoard({"totalPlayers": 0, "data": []})
        return data
