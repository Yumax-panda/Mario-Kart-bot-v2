from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from discord import Webhook

    from mk8dx.lounge.player import Player
    from mk8dx.lounge.types.client import LoungeClient as ILoungeClient
    from repository.config import Config
    from repository.types.repository import Repository as IRepository
    from service.types.services import Service as IService
    from utils.constants import Season


__all__ = ("BaseHandler",)


class BaseHandler(metaclass=ABCMeta):
    """全てのハンドラの基底クラス.
    共通するメソッドやプロパティを定義している.
    """

    if TYPE_CHECKING:
        config: Config
        lc: ILoungeClient
        repo: IRepository
        srv: IService
        session: ClientSession
        _webhook_token: str

    @abstractmethod
    async def get_players_by_user_ids(
        self,
        user_ids: list[int],
        season: Season | None = None,
    ) -> list[tuple[int, Player | None]]:
        """複数のdiscord IDからプレイヤー情報を取得する.
        discord IDがリンクされている場合はリンクされているIDで取得し, IDを紐づけて返す.

        Parameters
        ----------
        user_ids : list[int]
            discord IDのリスト
        season : Season | None, optional
            シーズン, by default None

        Returns
        -------
        list[tuple[int, Player | None]]
            discord IDとプレイヤー情報のタプルのリスト
        """
        ...

    @abstractmethod
    async def get_players_by_friend_codes(
        self,
        friend_codes: list[str],
        season: Season | None = None,
    ) -> list[tuple[str, Player | None]]:
        """複数のフレンドコードからプレイヤー情報を取得する.

        Parameters
        ----------
        friend_codes : list[str]
            フレンドコードのリスト
        season : Season | None, optional
            シーズン, by default None

        Returns
        -------
        list[tuple[str, Player | None]]
            フレンドコードとプレイヤー情報のタプルのリスト
        """
        ...

    @property
    @abstractmethod
    def webhook(self) -> Webhook:
        """ログを送信するためのWebhookを取得する.

        Returns
        -------
        Webhook
            ログを送信するためのWebhook
        """
        ...

    @abstractmethod
    async def setup_repository(self) -> None:
        """リポジトリの初期化処理を行う."""
        ...
