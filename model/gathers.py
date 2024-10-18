from __future__ import annotations

from typing import Literal, TypedDict

from sqlalchemy import BigInteger, Column, Integer, String, Table, UniqueConstraint

from .core import GATHERS_TABLE_NAME, metadata

__all__ = (
    "ParticipationType",
    "GatherItem",
    "gathers",
)

ParticipationType = Literal["c", "t", "s"]


class GatherItem(TypedDict):
    guild_id: int
    user_id: int
    type: ParticipationType
    hour: int


gathers = Table(
    GATHERS_TABLE_NAME,
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    # 挙手しているサーバーのID. サーバーを登録してない場合があるので, relationshipは使っていない.
    Column("guild_id", BigInteger),
    # 挙手しているユーザーのID (discord ID).
    Column("user_id", BigInteger),
    # 挙手の種類. can: c, tentative: t, substitute: s. 今後の拡張を考慮して3文字にしている.
    Column("type", String(3)),
    # 挙手している時間.
    Column("hour", Integer),
    # guild_id, user_id, hourの組み合わせがユニークであることを保証する.
    UniqueConstraint("guild_id", "user_id", "hour"),
)
