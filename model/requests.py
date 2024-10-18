from __future__ import annotations

from typing import Final, TypeAlias, TypedDict

from sqlalchemy import BigInteger, Column, Integer, Table, Text

from .core import REQUESTS_TABLE_NAME, metadata

__all__ = ("RequestPayload", "TargetUserPayload", "REQUESTS_TABLE_NAME")


class TargetUserPayload(TypedDict):
    fc: str
    name: str
    nsa_id: str


RequestPayload: TypeAlias = list[TargetUserPayload]

requests = Table(
    REQUESTS_TABLE_NAME,
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", BigInteger),
    Column("target_user_name", Text),
    Column("target_user_switch_fc", Text),
    Column("target_user_nsa_id", Text),
)
