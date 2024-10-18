from typing import Final, TypedDict

from sqlalchemy import BIGINT, Column, DateTime, Table, Text

from .core import NSO_TOKENS_TABLE_NAME, metadata

__all__ = (
    "NSOTokenPayload",
    "NSO_TOKENS_TABLE_NAME",
)


class NSOTokenPayload(TypedDict):
    key: str
    value: str
    __expires: int


nso_tokens = Table(
    NSO_TOKENS_TABLE_NAME,
    metadata,
    # ユーザーのdiscord ID.
    Column("user_id", BIGINT, primary_key=True),
    # Nintendo Switch Onlineのトークン.
    Column("token", Text, nullable=False),
    # トークンの有効期限.
    Column("expires_at", DateTime, nullable=False),
)
