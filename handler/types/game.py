from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

__all__ = ("GameHandler",)

if TYPE_CHECKING:
    from discord import Role

    from utils.types import HybridContext


class GameHandler(metaclass=ABCMeta):
    @abstractmethod
    async def game_start(self, ctx: HybridContext, enemy: str, role: Role | None) -> None: ...
