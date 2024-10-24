from __future__ import annotations

from asyncio import Semaphore
from functools import wraps
from typing import TYPE_CHECKING, Awaitable, Callable, Concatenate, Generic, ParamSpec, TypeVar

__all__ = ("RateLimit",)

if TYPE_CHECKING:
    from core import Cog
    from discord import ApplicationContext

    from utils.types import Context, HybridContext

CogT = TypeVar("CogT", bound="Cog")
T = TypeVar("T", str, int)
RT = TypeVar("RT")
CT = TypeVar("CT", "ApplicationContext", "Context", "HybridContext")
P = ParamSpec("P")


class RateLimit(Generic[T]):
    """コマンドにレートリミットを導入するためのクラス.
    `discord.ext.commands.max_concurrency`は別のコマンドに対して制御できないため独自に実装している.
    """

    __slots__ = (
        "__map",
        "get_key",
        "max_concurrency",
    )

    if TYPE_CHECKING:
        __map: dict[T, Semaphore]
        get_key: Callable[[HybridContext], T]
        max_concurrency: int

    def __init__(
        self,
        get_key: Callable[[HybridContext], T],
        max_concurrency: int = 1,
    ) -> None:
        self.__map = {}
        self.get_key = get_key
        self.max_concurrency = max_concurrency

    def limited(
        self,
        func: Callable[Concatenate[CogT, CT, P], Awaitable[RT]],
    ) -> Callable[Concatenate[CogT, CT, P], Awaitable[RT]]:
        """このデコレータでラップされた関数は、指定されたキーに対して最大同時実行数を制限する.

        Parameters
        ----------
        func : Callable[Concatenate[CogT, CT, P], Awaitable[RT]]
            コマンドのコールバック.

        Returns
        -------
        Callable[Concatenate[CogT, CT, P], Awaitable[RT]]
            ラップされた関数.
        """

        @wraps(func)
        async def wrapper(cog: CogT, ctx: CT, *args: P.args, **kwargs: P.kwargs) -> RT:
            key = self.get_key(ctx)

            try:
                sem = self.__map[key]
            except KeyError:
                sem = self.__map[key] = Semaphore(self.max_concurrency)

            async with sem:
                return await func(cog, ctx, *args, **kwargs)

        return wrapper
