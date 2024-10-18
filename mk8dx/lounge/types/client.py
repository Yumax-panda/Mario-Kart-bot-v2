from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Literal

__all__ = (
    "SortBy",
    "LoungeClient",
)

if TYPE_CHECKING:
    from utils.constants import Season

    from ..leaderboard import LeaderBoard
    from ..player import Player, PlayerDetails
    from ..utils import Search

SortBy = Literal[
    "name",
    "mmr",
    "max_mmr",
    "events_played",
    "average_score_no_sq",
    "win_rate",
    "win_loss_last_10",
    "gain_last_10",
    "average_score_no_sq_last_10",
]


class LoungeClient(metaclass=ABCMeta):
    @abstractmethod
    async def get_player(
        self,
        player_id: int | str | None = None,
        name: str | None = None,
        mkc_id: int | str | None = None,
        discord_id: int | str | None = None,
        fc: str | None = None,
        season: Season | None = None,
    ) -> Player | None:
        """Lounge APIからプレイヤー情報を取得する. 一度取得した情報はキャッシュされる.

        ref: https://github.com/VikeMK/Lounge-API/blob/37c5a06039d9a40806cc57f9663b0d243e29a210/src/Lounge.Web/Controllers/PlayersController.cs#L45

        Parameters
        ----------
        player_id : int | str | None, optional
            プレイヤーID, by default None
        name : str | None, optional
            プレイヤー名, by default None
        mkc_id : | int | str | None, optional
            Mario Kart CentralのID, by default None
        discord_id : int | str | None, optional
            DiscordのID, by default None
        fc : str | None, optional
            フレンドコード, by default None. dddd-dddd-dddd形式.
        season : Season | None, optional
            シーズン, by default None. Noneの場合は最新のシーズン.

        Returns
        -------
        Player | None
            プレイヤー情報
        """
        ...

    @abstractmethod
    async def get_player_details(
        self,
        player_id: int | str | None = None,
        name: str | None = None,
        season: Season | None = None,
    ) -> PlayerDetails | None:
        """Lounge APIからプレイヤー詳細情報を取得する. 一度取得した情報はキャッシュされる.

        ref: https://github.com/VikeMK/Lounge-API/blob/37c5a06039d9a40806cc57f9663b0d243e29a210/src/Lounge.Web/Controllers/PlayersController.cs#L85

        Parameters
        ----------
        player_id : int | str | None, optional
            プレイヤーID, by default None
        name : str | None, optional
            プレイヤー名, by default None
        season : Season | None, optional
            シーズン, by default None. Noneの場合は最新のシーズン.

        Returns
        -------
        PlayerDetails | None
            プレイヤー詳細情報
        """
        ...

    @abstractmethod
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
        """Lounge APIからリーダーボード情報を取得する.

        ref: https://github.com/VikeMK/Lounge-API/blob/37c5a06039d9a40806cc57f9663b0d243e29a210/src/Lounge.Web/Controllers/PlayersController.cs#L128

        Parameters
        ----------
        season : Season | None, optional
            シーズン, by default None. Noneの場合は最新のシーズン.
        skip : int, optional
            ソートされたリーダーボードの先頭からスキップする数, by default 0
        page_size : int, optional
            検索で該当するプレイヤー全体のうち, 実際にデータを取得する数. by default 50
            0 <= page_size <= 100を満たす必要がある.
        search : Search | None, optional
            関連するプレイヤーを検索するためのクエリ, by default None
            mkc_ic, discord_id, Nintendo Switchのフレンドコードを指定できる.
        sort_by : SortBy | None, optional
            ソートするためのキー, by default None
        country : str | None, optional
            検索するプレイヤーの国籍, by default None
        min_mmr : int | None, optional
            検索するプレイヤーの最小MMR, by default None
        max_mmr : int | None, optional
            検索するプレイヤーの最大MMR, by default None
        min_events_played : int | None, optional
            検索するプレイヤーの模擬回数の最小値, by default None
        max_events_played : int | None, optional
            検索するプレイヤーの模擬回数の最大値, by default None

        Returns
        -------
        LeaderBoard
            リーダーボード情報.

        Notes
        -----
        これはget_playerとget_player_detailsとは異なり, 使用する機会が少ないためキャッシュは行わない.
        """
        ...
