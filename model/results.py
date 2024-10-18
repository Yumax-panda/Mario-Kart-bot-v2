from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias, TypedDict

from sqlalchemy import BigInteger, Column, DateTime, Integer, Table, Text

from .core import RESULTS_TABLE_NAME, metadata

__all__ = (
    "ResultItem",
    "ResultItemWithID",
    "Results",
    "ResultPayload",
)

if TYPE_CHECKING:
    from datetime import datetime


class ResultItem(TypedDict):
    date: datetime
    enemy: str
    enemyScore: int
    score: int


class ResultItemWithID(ResultItem):
    id: int


Results: TypeAlias = list[ResultItem]


class ResultPayload(TypedDict):
    data: list[ResultItem]


results = Table(
    RESULTS_TABLE_NAME,
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    # 戦績を登録しているサーバーのID (discordのguild_idと同じ).
    Column("guild_id", BigInteger),
    # 対戦日時. (JST)
    Column("played_at", DateTime),
    # 自チームの得点.
    Column("score", Integer),
    # 相手チームの名前.
    Column("enemy", Text),
    # 相手チームの得点.
    Column("enemy_score", Integer),
)
