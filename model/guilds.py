from sqlalchemy import BigInteger, Column, Table, Text

from .core import GUILDS_TABLE_NAME, metadata

__all__ = ("guilds",)


guilds = Table(
    GUILDS_TABLE_NAME,
    metadata,
    # サーバーのID. (discordのguild_idと同じ)
    Column("id", BigInteger, primary_key=True),
    # チーム名.
    Column("name", Text),
)
