from __future__ import annotations

from typing import TypedDict

from sqlalchemy import BigInteger, Column, Table, Text

from .core import SESSION_TOKENS_TABLE_NAME, metadata

__all__ = (
    "SessionTokenPayload",
    "SESSION_TOKENS_TABLE_NAME",
)


class SessionTokenPayload(TypedDict):
    key: str
    value: str


session_tokens = Table(
    SESSION_TOKENS_TABLE_NAME,
    metadata,
    # ユーザーのdiscord ID.
    Column("user_id", BigInteger, primary_key=True),
    # セッショントークン.
    Column("token", Text, nullable=False),
)
