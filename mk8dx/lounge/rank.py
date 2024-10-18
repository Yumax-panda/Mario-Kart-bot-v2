from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, TypeVar

from discord import Color, Embed

from utils.constants import CURRENT_SEASON, Season

from .types.rank import Rank as RankPayload
from .utils import BaseModel

__all__ = ("Rank",)

if TYPE_CHECKING:
    from .types.rank import Division

RT = TypeVar("RT", bound="Rank")


class Rank(BaseModel):

    __slots__ = (
        "division",
        "level",
        "url",
        "color",
    )

    if TYPE_CHECKING:
        division: Division
        level: int | None
        url: str
        color: Color

    def __init__(self, data: RankPayload) -> None:
        self.division = data["division"]
        self.level = data.get("level")

        rank_data = get_rank_data(self.division)
        self.url = rank_data["url"]
        self.color = Color(rank_data["color"])

    def to_dict(self) -> RankPayload:
        return {
            "division": self.division,
            "level": self.level,
        }

    @classmethod
    def from_nick(cls: type[RT], nick: str) -> RT:

        if " " in nick:
            division, level = nick.split(" ", maxsplit=1)
            data: RankPayload = {
                "division": division,  # type: ignore
                "level": int(level),
            }
            return cls(data)
        else:
            data = {
                "division": nick,  # type: ignore
            }
            return cls(data)

    @classmethod
    def from_mmr(cls: type[RT], mmr: int | float, season: Season | None = None) -> RT:
        """MMRに対応するランクを取得する.

        Parameters
        ----------
        mmr : int | float
            MMR
        season : Season | None, optional
            シーズン, by default None

        Returns
        -------
        Rank
            MMRに対応するランク
        """
        _season = season or CURRENT_SEASON

        if _season == 5:
            if mmr >= 14000:
                return cls.from_nick("Grandmaster")
            elif mmr >= 13000:
                return cls.from_nick("Master")
            elif mmr >= 12000:
                return cls.from_nick("Diamond 2")
            elif mmr >= 11000:
                return cls.from_nick("Diamond 1")
            elif mmr >= 10000:
                return cls.from_nick("Sapphire")
            elif mmr >= 9000:
                return cls.from_nick("Platinum 2")
            elif mmr >= 8000:
                return cls.from_nick("Platinum 1")
            elif mmr >= 7000:
                return cls.from_nick("Gold 2")
            elif mmr >= 6000:
                return cls.from_nick("Gold 1")
            elif mmr >= 5000:
                return cls.from_nick("Silver 2")
            elif mmr >= 4000:
                return cls.from_nick("Silver 1")
            elif mmr >= 3000:
                return cls.from_nick("Bronze 2")
            elif mmr >= 2000:
                return cls.from_nick("Bronze 1")
            elif mmr >= 1000:
                return cls.from_nick("Iron 2")
            else:
                return cls.from_nick("Iron 1")
        elif _season <= 7:
            if mmr >= 15000:
                return cls.from_nick("Grandmaster")
            elif mmr >= 14000:
                return cls.from_nick("Master")
            elif mmr >= 13000:
                return cls.from_nick("Diamond 2")
            elif mmr >= 12000:
                return cls.from_nick("Diamond 1")
            elif mmr >= 11000:
                return cls.from_nick("Sapphire 2")
            elif mmr >= 10000:
                return cls.from_nick("Sapphire 1")
            elif mmr >= 9000:
                return cls.from_nick("Platinum 2")
            elif mmr >= 8000:
                return cls.from_nick("Platinum 1")
            elif mmr >= 7000:
                return cls.from_nick("Gold 2")
            elif mmr >= 6000:
                return cls.from_nick("Gold 1")
            elif mmr >= 5000:
                return cls.from_nick("Silver 2")
            elif mmr >= 4000:
                return cls.from_nick("Silver 1")
            elif mmr >= 3000:
                return cls.from_nick("Bronze 2")
            elif mmr >= 2000:
                return cls.from_nick("Bronze 1")
            elif mmr >= 1000:
                return cls.from_nick("Iron 2")
            else:
                return cls.from_nick("Iron 1")
        else:
            if mmr >= 17000:
                return cls.from_nick("Grandmaster")
            elif mmr >= 16000:
                return cls.from_nick("Master")
            elif mmr >= 15000:
                return cls.from_nick("Diamond 2")
            elif mmr >= 14000:
                return cls.from_nick("Diamond 1")
            elif mmr >= 13000:
                return cls.from_nick("Ruby 2")
            elif mmr >= 12000:
                return cls.from_nick("Ruby 1")
            elif mmr >= 11000:
                return cls.from_nick("Sapphire 2")
            elif mmr >= 10000:
                return cls.from_nick("Sapphire 1")
            elif mmr >= 9000:
                return cls.from_nick("Platinum 2")
            elif mmr >= 8000:
                return cls.from_nick("Platinum 1")
            elif mmr >= 7000:
                return cls.from_nick("Gold 2")
            elif mmr >= 6000:
                return cls.from_nick("Gold 1")
            elif mmr >= 5000:
                return cls.from_nick("Silver 2")
            elif mmr >= 4000:
                return cls.from_nick("Silver 1")
            elif mmr >= 3000:
                return cls.from_nick("Bronze 2")
            elif mmr >= 2000:
                return cls.from_nick("Bronze 1")
            elif mmr >= 1000:
                return cls.from_nick("Iron 2")
            else:
                return cls.from_nick("Iron 1")

    @property
    def name(self) -> str:
        return f"{self.division} {self.level}" if self.level is not None else self.division

    def to_embed(self) -> Embed:
        """ランクに対応する色と画像を設定したEmbedを取得する.

        Returns
        -------
        Embed
            ランクに対応する色と画像を設定したEmbed
        """
        return Embed(color=self.color, thumbnail=self.url)


class RankDataItem(TypedDict):
    color: int
    url: str


def get_rank_data(division: "Division") -> RankDataItem:
    """Divisionに対応するランクデータを取得する.

    Parameters
    ----------
    division : Division
        取得するデータのDivision

    Returns
    -------
    RankDataItem
        Divisionに対応するデータ
    """
    # これは冗長に見えるが, 変数が予期しないタイミングで変更されることを防いでいる.
    data: dict[Division, RankDataItem] = {
        "Grandmaster": {"color": 0xA3022C, "url": "https://i.imgur.com/EWXzu2U.png"},
        "Master": {"color": 0xD9E1F2, "url": "https://i.imgur.com/3yBab63.png"},
        "Diamond": {"color": 0xBDD7EE, "url": "https://i.imgur.com/RDlvdvA.png"},
        "Ruby": {"color": 0xD51C5E, "url": "https://i.imgur.com/WU2NlJQ.png"},
        "Sapphire": {"color": 0x286CD3, "url": "https://i.imgur.com/bXEfUSV.png"},
        "Platinum": {"color": 0x3FABB8, "url": "https://i.imgur.com/8v8IjHE.png"},
        "Gold": {"color": 0xFFD966, "url": "https://i.imgur.com/6yAatOq.png"},
        "Silver": {"color": 0xD9D9D9, "url": "https://i.imgur.com/xgFyiYa.png"},
        "Bronze": {"color": 0xC65911, "url": "https://i.imgur.com/DxFLvtO.png"},
        "Iron": {"color": 0x817876, "url": "https://i.imgur.com/AYRMVEu.png"},
    }
    return data[division]
