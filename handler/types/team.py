from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

__all__ = ("TeamHandler",)

if TYPE_CHECKING:
    from discord import ApplicationContext, Role

    from utils.constants import Season


class TeamHandler(metaclass=ABCMeta):
    @abstractmethod
    async def team_mmr(self, ctx: ApplicationContext, role: Role, season: Season | None = None) -> None: ...
    @abstractmethod
    async def team_peak_mmr(self, ctx: ApplicationContext, role: Role, season: Season | None = None) -> None: ...
    @abstractmethod
    async def team_mkc(self, ctx: ApplicationContext, role: Role) -> None: ...
    @abstractmethod
    async def team_name_set(self, ctx: ApplicationContext, name: str) -> None: ...
    @abstractmethod
    async def team_name_show(self, ctx: ApplicationContext) -> None: ...
