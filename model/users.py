from __future__ import annotations

from sqlalchemy import BigInteger, Column, Table

from .core import USERS_TABLE_NAME, metadata

__all__ = ("users",)


users = Table(
    USERS_TABLE_NAME,
    metadata,
    # ユーザーのID. (discord　IDと同じ)
    Column("id", BigInteger, primary_key=True),
    # ラウンジに登録しているアカウントのdiscord ID.
    Column("lounge_id", BigInteger),
)
