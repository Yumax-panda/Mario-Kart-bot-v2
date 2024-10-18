from __future__ import annotations

from typing import TYPE_CHECKING, Final, TypedDict, TypeVar

from dateutil.parser import isoparse  # type: ignore
from discord import Embed, File

from figure.stats import create_mmr_history_graph

from .errors import NoMMRFound
from .rank import Rank
from .utils import BaseModel

if TYPE_CHECKING:
    from .types.player import BasePlayer as BasePlayerPayload, Player as PlayerPayload, PlayerDetails as PlayerDetailsPayload

    class Stats(TypedDict):
        embeds: list[Embed]
        files: list[File]

else:
    Stats = dict[str, ...]


PlayerPayloadT = TypeVar("PlayerPayloadT", bound="BasePlayerPayload")


MKC_URL: Final[str] = "https://www.mariokartcentral.com/mkc/registry/users/"
LOUNGE_WEB: Final[str] = "https://www.mk8dx-lounge.com/PlayerDetails/"

__all__ = (
    "PlayerTag",
    "BasePlayer",
    "PartialPlayer",
    "Player",
    "PlayerDetails",
    "LeaderBoardPlayer",
)

if TYPE_CHECKING:
    from datetime import datetime

    from .types.player import (
        BasePlayer as BasePlayerPayload,
        LeaderBoardPlayer as LeaderBoardPlayerPayload,
        MmrChange as MmrChangePayload,
        NameChange as NameChangePayload,
        PartialPlayer as PartialPlayerPayload,
        Player as PlayerPayload,
        PlayerDetails as PlayerDetailsPayload,
        ReasonType,
    )
    from .types.tier import TierType


class MmrChange(BaseModel):

    __slots__ = (
        "change_id",
        "new_mmr",
        "mmr_delta",
        "reason",
        "time",
        "score",
        "partner_scores",
        "partner_ids",
        "tier",
        "numTeams",
    )

    if TYPE_CHECKING:
        change_id: int | None
        new_mmr: int
        mmr_delta: int
        reason: ReasonType
        time: datetime
        score: int | None
        partner_scores: list[int]
        partner_ids: list[int]
        tier: TierType | None
        numTeams: int | None

    def __init__(self, data: MmrChangePayload) -> None:
        self.change_id = data.get("changeId")
        self.new_mmr = data["newMmr"]
        self.mmr_delta = data["mmrDelta"]
        self.reason = data["reason"]
        self.time = isoparse(data["time"])
        self.score = data.get("score")
        # NOTE: data.get("partnerScores") or [] としているのは、
        # data["partnerScores"]がNoneの場合に空リストを返すため
        self.partner_scores = data.get("partnerScores") or []
        self.partner_ids = data.get("partnerIds") or []
        self.tier = data.get("tier")
        self.numTeams = data.get("numTeams")

    def to_dict(self) -> MmrChangePayload:
        return {
            "changeId": self.change_id,
            "newMmr": self.new_mmr,
            "mmrDelta": self.mmr_delta,
            "reason": self.reason,
            "time": self.time.isoformat(),
            "score": self.score,
            "partnerScores": self.partner_scores,
            "partnerIds": self.partner_ids,
            "tier": self.tier,
            "numTeams": self.numTeams,
        }


class NameChange(BaseModel):

    __slots__ = ("name", "changed_on")

    if TYPE_CHECKING:
        name: str
        changed_on: datetime

    def __init__(self, data: NameChangePayload) -> None:
        self.name = data["name"]
        self.changed_on = isoparse(data["changedOn"])

    def to_dict(self) -> NameChangePayload:
        return {
            "name": self.name,
            "changedOn": self.changed_on.isoformat(),
        }


class BasePlayer(BaseModel):

    __slots__ = (
        "name",
        "mmr",
    )

    if TYPE_CHECKING:
        name: str
        mmr: int | None

    def __init__(self, data: PlayerPayloadT) -> None:
        self.name = data["name"]
        self.mmr = data.get("mmr")  # type: ignore


class Player(BasePlayer):

    __slots__ = (
        "name",
        "mmr",
        "id",
        "mkc_id",
        "discord_id",
        "country_code",
        "switch_fc",
        "is_hidden",
        "max_mmr",
        "_linked_id",
    )

    if TYPE_CHECKING:
        name: str
        mmr: int | None
        id: int
        mkc_id: int
        discord_id: str | None
        country_code: str | None
        switch_fc: str | None
        is_hidden: bool
        max_mmr: int | None
        _linked_id: str | None

    def __init__(self, data: PlayerPayload) -> None:
        super().__init__(data)
        self.id = int(data["id"])
        self.mkc_id = int(data["mkcId"])
        self.discord_id = data.get("discordId")
        self.country_code = data.get("countryCode")
        self.switch_fc = data.get("switchFc")
        self.is_hidden = data["isHidden"]
        self.max_mmr = data.get("maxMmr")
        self.link_id(data.get("linkedId") or data.get("discordId"))

    @property
    def lounge_url(self) -> str:
        return f"{LOUNGE_WEB}{self.id}"

    @property
    def mkc_url(self) -> str:
        return f"{MKC_URL}{self.mkc_id}"

    @property
    def is_placement(self) -> bool:
        return self.is_hidden or self.mmr is None

    @property
    def linked_id(self) -> str | None:
        """プレイヤーと紐づいているdiscord IDを返す.
        Player.link_id()で指定することを想定している.
        デフォルトはPlayer.discord_idと同じ.

        Returns
        -------
        str | None
            プレイヤーと紐づいているdiscord ID.
            デフォルトはPlayer.discord_idと同じ.
        """
        return self._linked_id

    def link_id(self, value: str | int | None) -> None:
        self._linked_id = str(value) if value is not None else None

    def to_dict(self) -> PlayerPayload:
        return {
            "name": self.name,
            "mmr": self.mmr,
            "id": self.id,
            "mkcId": self.mkc_id,
            "discordId": self.discord_id,
            "countryCode": self.country_code,
            "switchFc": self.switch_fc,
            "isHidden": self.is_hidden,
            "maxMmr": self.max_mmr,
            "linkedId": self.linked_id,
        }


class PartialPlayer(BasePlayer):

    __slots__ = ("name", "mmr", "mkc_id", "events_played", "discord_id")

    if TYPE_CHECKING:
        name: str
        mmr: int | None
        mkc_id: int
        events_played: int
        discord_id: str | None

    def __init__(self, data: PartialPlayerPayload) -> None:
        super().__init__(data)
        self.mkc_id = int(data["mkcId"])
        self.events_played = data["eventsPlayed"]
        self.discord_id = data.get("discordId")

    def to_dict(self) -> PartialPlayerPayload:
        return {
            "name": self.name,
            "mmr": self.mmr,
            "mkcId": self.mkc_id,
            "eventsPlayed": self.events_played,
            "discordId": self.discord_id,
        }


class PlayerDetails(BasePlayer):

    __slots__ = (
        "name",
        "mmr",
        "player_id",
        "mkc_id",
        "country_code",
        "country_name",
        "switch_fc",
        "is_hidden",
        "season",
        "max_mmr",
        "overall_rank",
        "events_played",
        "win_rate",
        "wins_last_ten",
        "losses_last_ten",
        "gain_loss_last_ten",
        "largest_gain",
        "largest_gain_table_id",
        "largest_loss",
        "largest_loss_table_id",
        "average_score",
        "average_last_ten",
        "partner_average",
        "mmr_changes",
        "name_history",
        "rank",
    )

    if TYPE_CHECKING:
        name: str
        mmr: int | None
        player_id: int
        mkc_id: int
        country_code: str | None
        country_name: str | None
        switch_fc: str | None
        is_hidden: bool
        season: int
        max_mmr: int | None
        overall_rank: int | None
        events_played: int
        win_rate: float | None
        wins_last_ten: int
        losses_last_ten: int
        gain_loss_last_ten: int | None
        largest_gain: int | None
        largest_gain_table_id: int | None
        largest_loss: int | None
        largest_loss_table_id: int | None
        average_score: float | None
        average_last_ten: float | None
        partner_average: float | None
        mmr_changes: list[MmrChange]
        name_history: list[NameChange]
        rank: Rank

    def __init__(self, data: PlayerDetailsPayload) -> None:
        super().__init__(data)
        self.player_id = int(data["playerId"])
        self.mkc_id = int(data["mkcId"])
        self.country_code = data.get("countryCode")
        self.country_name = data.get("countryName")
        self.switch_fc = data.get("switchFc")
        self.is_hidden = data["isHidden"]
        self.season = data["season"]
        self.max_mmr = data.get("maxMmr")
        self.overall_rank = data.get("overallRank")
        self.events_played = data["eventsPlayed"]
        self.win_rate = data.get("winRate")
        self.wins_last_ten = data["winsLastTen"]
        self.losses_last_ten = data["lossesLastTen"]
        self.gain_loss_last_ten = data.get("gainLossLastTen")
        self.largest_gain = data.get("largestGain")
        self.largest_gain_table_id = data.get("largestGainTableId")
        self.largest_loss = data.get("largestLoss")
        self.largest_loss_table_id = data.get("largestLossTableId")
        self.average_score = data.get("averageScore")
        self.average_last_ten = data.get("averageLastTen")
        self.partner_average = data.get("partnerAverage")
        self.mmr_changes = [MmrChange(x) for x in data["mmrChanges"]]
        self.name_history = [NameChange(x) for x in data["nameHistory"]]
        self.rank = Rank.from_nick(data["rank"])

    def to_dict(self) -> PlayerDetailsPayload:
        return {
            "name": self.name,
            "mmr": self.mmr,
            "playerId": self.player_id,
            "mkcId": self.mkc_id,
            "countryCode": self.country_code,
            "countryName": self.country_name,
            "switchFc": self.switch_fc,
            "isHidden": self.is_hidden,
            "season": self.season,
            "maxMmr": self.max_mmr,
            "overallRank": self.overall_rank,
            "eventsPlayed": self.events_played,
            "winRate": self.win_rate,
            "winsLastTen": self.wins_last_ten,
            "lossesLastTen": self.losses_last_ten,
            "gainLossLastTen": self.gain_loss_last_ten,
            "largestGain": self.largest_gain,
            "largestGainTableId": self.largest_gain_table_id,
            "largestLoss": self.largest_loss,
            "largestLossTableId": self.largest_loss_table_id,
            "averageScore": self.average_score,
            "averageLastTen": self.average_last_ten,
            "partnerAverage": self.partner_average,
            "mmrChanges": [x.to_dict() for x in self.mmr_changes],
            "nameHistory": [x.to_dict() for x in self.name_history],
            "rank": self.rank.name,
        }

    def to_stats(self, display_name: str | None = None) -> Stats:
        """プレイヤー情報を表したStatsを返す.


        Parameters
        ----------
        display_name : str | None
            表示名. デフォルトはNone.

        Returns
        -------
        Stats
            プレイヤー情報を表したStats.

        Raises
        ------
        NoMMRFound
            MMRが見つからない場合に発生.
        """

        if self.mmr is None:
            raise NoMMRFound

        e = self.rank.to_embed()

        name = display_name or self.name
        e.title = f"{name}'s stats"
        season = self.season
        url = f"{LOUNGE_WEB}{self.player_id}"

        def fmt(v: float) -> str:
            return "{:.1f}".format(v)

        if season is not None:
            e.title += f" | Season {season}"
            url += f"?season={season}"

        e.description = f"[{self.name}]({url})"

        if self.overall_rank is not None:
            e.add_field(name="Rank", value=str(self.overall_rank))

        e.add_field(name="MMR", value=str(self.mmr))

        if self.max_mmr is not None:
            e.add_field(name="Peak MMR", value=str(self.max_mmr))

        if self.win_rate is not None:
            e.add_field(name="Win Rate", value=fmt(self.win_rate * 100))

        e.add_field(name="W - L", value=f"{self.wins_last_ten} - {self.losses_last_ten}")

        if self.gain_loss_last_ten is not None:
            e.add_field(name="+/-", value=str(self.gain_loss_last_ten))

        if self.average_score is not None:
            e.add_field(name="Avg. Score", value=fmt(self.average_score))

        if self.partner_average is not None:
            e.add_field(name="Partner Avg.", value=fmt(self.partner_average))

        e.add_field(name="Events Played", value=str(self.events_played))

        if len(self.name_history) >= 2:
            prev = self.name_history[1]
            e.add_field(name="Previous Name", value=prev.name)

        events = self.mmr_changes[::-1]
        deleted_ids: list[int] = [e.change_id for e in events if e.reason == "TableDelete" and e.change_id is not None]

        mmr_history: list[int] = []

        for event in events:
            if event.reason in ("Table", "Placement") and event.change_id not in deleted_ids:
                mmr_history.append(event.new_mmr)

        data: Stats = {"embeds": [e], "files": []}

        if len(mmr_history) > 2:
            fp = create_mmr_history_graph(mmr_history, season)
            file = File(fp, filename="stats.png")
            data["files"].append(file)
            e.set_image(url="attachment://stats.png")

        return data


class LeaderBoardPlayer(BasePlayer):

    __slots__ = (
        "name",
        "mmr",
        "id",
        "wins_last_ten",
        "losses_last_ten",
        "events_played",
        "overall_rank",
        "country_code",
        "max_mmr",
        "win_rate",
        "gain_loss_last_ten",
        "largest_gain",
        "largest_loss",
        "max_rank",
        "max_mmr_rank",
    )

    if TYPE_CHECKING:
        name: str
        mmr: int | None
        id: int
        wins_last_ten: int
        losses_last_ten: int
        events_played: int
        overall_rank: int | None
        country_code: str | None
        max_mmr: int | None
        win_rate: float | None
        gain_loss_last_ten: int | None
        largest_gain: int | None
        largest_loss: int | None
        max_rank: Rank | None
        max_mmr_rank: Rank | None

    def __init__(self, data: LeaderBoardPlayerPayload) -> None:
        super().__init__(data)
        self.id = data["id"]
        self.wins_last_ten = data["winsLastTen"]
        self.losses_last_ten = data["lossesLastTen"]
        self.events_played = data["eventsPlayed"]
        self.overall_rank = data.get("overallRank")
        self.country_code = data.get("countryCode")
        self.max_mmr = data.get("maxMmr")
        self.win_rate = data.get("winRate")
        self.gain_loss_last_ten = data.get("gainLossLastTen")
        self.largest_gain = data.get("largestGain")
        self.largest_loss = data.get("largestLoss")

        if (max_rank := data.get("maxRank")) is not None:
            self.max_rank = Rank(max_rank)
        else:
            self.max_rank = None

        if (max_mmr_rank := data.get("maxMmrRank")) is not None:
            self.max_mmr_rank = Rank(max_mmr_rank)
        else:
            self.max_mmr_rank = None

    def to_dict(self) -> LeaderBoardPlayerPayload:
        return {
            "name": self.name,
            "mmr": self.mmr,
            "id": self.id,
            "winsLastTen": self.wins_last_ten,
            "lossesLastTen": self.losses_last_ten,
            "eventsPlayed": self.events_played,
            "overallRank": self.overall_rank,
            "countryCode": self.country_code,
            "maxMmr": self.max_mmr,
            "winRate": self.win_rate,
            "gainLossLastTen": self.gain_loss_last_ten,
            "largestGain": self.largest_gain,
            "largestLoss": self.largest_loss,
            "maxRank": self.max_rank.to_dict() if self.max_rank else None,
            "maxMmrRank": self.max_mmr_rank.to_dict() if self.max_mmr_rank else None,
        }
