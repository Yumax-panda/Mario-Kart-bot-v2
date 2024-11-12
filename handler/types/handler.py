from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from . import (
    AdminHandler,
    BaseHandler,
    BookmarkHandler,
    FriendHandler,
    RecruitHandler,
    ResultHandler,
    TeamHandler,
    UtilityHandler,
)

__all__ = ("Handler",)

if TYPE_CHECKING:
    from mk8dx.lounge.types.client import LoungeClient as ILoungeClient
    from repository.types.repository import Repository as IRepository
    from service.types.services import Service as IService


class Handler(
    BaseHandler,
    AdminHandler,
    BookmarkHandler,
    FriendHandler,
    RecruitHandler,
    ResultHandler,
    TeamHandler,
    UtilityHandler,
):
    @abstractmethod
    def __init__(
        self,
        webhook_token: str,
        lc: ILoungeClient,
        repo: IRepository,
        srv: IService,
    ) -> None: ...
