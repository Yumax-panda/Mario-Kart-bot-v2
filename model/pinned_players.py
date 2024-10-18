from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias, TypedDict

from sqlalchemy import BIGINT, Column, Integer, Table, Text, UniqueConstraint

from .core import PINNED_PLAYERS_TABLE_NAME, metadata

__all__ = (
    "PinnedPlayerPayload",
    "PinnedPlayerItem",
    "PinnedPlayer",
    "PINNED_PLAYERS_TABLE_NAME",
)

# "mkc_id nick_name"のリストになっている
PinnedPlayerPayload: TypeAlias = list[str]


class PinnedPlayerItem(TypedDict):
    """ブックマークされたプレイヤーの情報を表す型.
    本来は`{id} {nick_name}`の形式の文字列で保存されているが,
    dictとして各々を分けた形の方が扱いやすいためこのモデルを定義.
    """

    id: str
    nick_name: str


class PinnedPlayer:

    __slots__ = (
        "id",
        "nick_name",
    )

    if TYPE_CHECKING:
        id: str
        nick_name: str

    def __init__(self, mkc_id: str, nick_name: str) -> None:
        self.id = mkc_id
        self.nick_name = nick_name

    @classmethod
    def from_dict(cls, data: PinnedPlayerItem) -> PinnedPlayer:
        return cls(data["id"], data["nick_name"])

    def to_dict(self) -> PinnedPlayerItem:
        return {"id": self.id, "nick_name": self.nick_name}

    @property
    def repr(self) -> str:
        return f"{self.id} {self.nick_name}"

    @classmethod
    def from_repr(cls, repr: str) -> PinnedPlayer:
        id, nick_name = repr.split(" ", maxsplit=1)
        return cls(id, nick_name)


pinned_players = Table(
    PINNED_PLAYERS_TABLE_NAME,
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    # ブックマークをしたユーザーのdiscord ID.
    Column("user_id", BIGINT),
    # ブックマークされたプレイヤーのID.
    Column("bookmarked_player_id", BIGINT),
    # ブックマークされたプレイヤーの表示名.
    Column("bookmarked_player_display_name", Text),
    # 同じプレイヤーを同じユーザーが登録しないように.
    UniqueConstraint("user_id", "bookmarked_player_id"),
)
