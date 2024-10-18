from __future__ import annotations

from typing import TYPE_CHECKING

from .admin import AdminHandler
from .bookmark import BookmarkHandler
from .core import BaseHandler
from .friend import FriendHandler
from .game import GameHandler
from .recruit import RecruitHandler
from .result import ResultHandler
from .team import TeamHandler
from .utility import UtilityHandler

if TYPE_CHECKING:
    from mk8dx.lounge.types.client import LoungeClient as ILoungeClient
    from repository.config import Config
    from repository.types.repository import Repository as IRepository
    from service.types.services import Service as IService


__all__ = ("Handler",)


class Handler(
    BaseHandler,
    AdminHandler,
    BookmarkHandler,
    FriendHandler,
    GameHandler,
    RecruitHandler,
    ResultHandler,
    TeamHandler,
    UtilityHandler,
):
    def __init__(self, config: Config, webhook_token: str, lc: ILoungeClient, srv: IService) -> None:
        # RepositoryはBotの起動後にセットアップする.
        self._webhook_token = webhook_token
        self.config = config
        self.lc = lc
        self.srv = srv
