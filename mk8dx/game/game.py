from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, ClassVar, Final, Iterable, TypedDict

from discord import ApplicationContext, Embed, Interaction, Member, User

from utils.constants import EmbedColor
from utils.format import format_banner_user_name, format_scores
from utils.parser import parse_natural_numbers

from .errors import GameNotFound
from .race import Race
from .rank import Rank
from .track import Track

__all__ = ("Game",)

ALLOWED_BOT_ID: Final[int] = 813078218344759326

if TYPE_CHECKING:
    from discord import Embed, Message
    from discord.abc import MessageableChannel as Channel

    from bot import Bot
    from utils.constants import Locale, LocaleDict
    from utils.types import HybridContext, HybridMessage

    class Options(TypedDict, total=False):
        penalties: list[int]
        re_picks: list[int]


class Game:
    TITLE: ClassVar[LocaleDict] = {
        "ja": "即時集計",
        "en-US": "Sokuji",
    }
    ARCHIVE_TITLE: ClassVar[LocaleDict] = {
        "ja": "アーカイブ",
        "en-US": "Archive",
    }

    if TYPE_CHECKING:
        races: list[Race]
        teams: list[str]
        banner_users: set[str]
        penalties: list[int]
        re_picks: list[int]
        message: HybridMessage | None
        is_archived: bool
        locale: Locale
        pending_track: Track | None

    def __init__(
        self,
        teams: list[str],
        banner_users: set[str] = set(),
        races: list[Race] = [],
        penalties: list[int] = [0, 0],
        re_picks: list[int] = [0, 0],
        message: Message | None = None,
        is_archived: bool = False,
        locale: Locale = "ja",
        pending_track: Track | None = None,
    ) -> None:
        self.races = races
        self.teams = teams
        self.banner_users = banner_users
        self.penalties = penalties
        self.re_picks = re_picks
        self.message = message
        self.is_archived = is_archived
        self.locale = locale
        self.pending_track = pending_track

    @staticmethod
    async def start(ctx: HybridContext, team_names: list[str], banner_users: Iterable[Member | User]) -> Game:
        """即時集計を開始する.

        Parameters
        ----------
        ctx : Context
            コンテキスト
        team_names : list[str]
            チーム名のリスト
        banner_users : Iterable[Member | User]
            OBSを使うユーザーのリスト

        Returns
        -------
        Game
            開始した即時集計
        """
        g = Game(teams=team_names, banner_users=set(map(format_banner_user_name, banner_users)))
        await g.resend(ctx)
        return g

    async def resend(self, ctx: HybridContext) -> None:
        """最新の即時情報を送信する.
        古い即時情報は削除される.

        Parameters
        ----------
        ctx : Context
            コンテキスト
        """
        if self.message is not None:
            await self.message.delete()

        embed = self.to_embed()

        if isinstance(ctx, ApplicationContext):
            resp = await ctx.respond(embed=embed)

            if isinstance(resp, Interaction):
                self.message = resp.message
            else:
                self.message = resp
        else:
            self.message = await ctx.send(embed=embed)

    def archive(self) -> None:
        """即時集計をアーカイブする."""
        self.is_archived = True

    def unarchive(self) -> None:
        """即時集計をアーカイブ解除する."""
        self.is_archived = False

    async def update(self) -> None:
        """即時集計を更新する.
        古い即時情報が存在する場合, それを上書きする.
        """
        if self.message is None:
            return

        message = await self.message.edit(embed=self.to_embed())
        self.message = message

    def change_enemy_name(self, name: str) -> None:
        """敵チームの名前を変更する.

        Parameters
        ----------
        name : str
            新しい敵チームの名前
        """
        self.teams[1] = name

    @staticmethod
    def from_message(message: HybridMessage) -> Game:
        """指定されたメッセージから即時データを取得する.
        必ず `Game.is_valid_message` でメッセージの妥当性を確認してから呼び出すこと.

        Parameters
        ----------
        message : Message | WebhookMessage
            即時集計のメッセージ

        Returns
        -------
        Game
            読み込んだ即時集計
        """
        embed = message.embeds[0].copy()
        locale = Game.get_locale(embed)
        team_tags: list[str] = embed.title.split("\n", maxsplit=1)[-1].split(" - ")  # type: ignore # see Game.is_valid_message
        is_archived = embed.author is not None and embed.author.name in Game.ARCHIVE_TITLE.values()
        banner_users = set()
        races: list[Race] = []

        options: Options = {}

        for field in embed.fields:
            numbers = parse_natural_numbers(field.value)

            # ペナルティ or コース重複の場合
            if field.name in ("Penalty", "Repick"):

                # [自チーム, 相手チーム] の順番で格納
                # NOTE: 本来はnumbersやoldの長さが2以上であることを保証すべきだが,
                # field名が"Penalty"や"Repick"であるときは必ず2つの数値が格納されているため
                # バリデーションを省略している.
                new: list[int] = [numbers[i] for i in range(1)]

                if field.name == "Penalty":
                    options["penalties"] = new
                else:
                    options["re_picks"] = new

            # OBSを使っているメンバーの取得
            elif field.name == "Members":
                value = field.value
                users = value.split("> @", maxsplit=1)[-1].split(", @")
                banner_users = set(users)

            # レース結果のパース
            else:
                track: Track | None = None
                if "-" in field.name:
                    name = field.name
                    nick = name[name.find("-") + 2 :]
                    track = Track.from_nick(nick)
                race = Race(ranks=[Rank(numbers[-6:]), Rank({i for i in range(1, 13)} - set(numbers[-6:]))], track=track)
                races.append(race)

        return Game(
            races=races,
            teams=team_tags,
            banner_users=banner_users,
            message=message,
            is_archived=is_archived,
            locale=locale,
            **options,
        )

    @staticmethod
    async def fetch(channel: Channel, allow_read_only: bool = False, allow_archived: bool = False) -> Game:
        """指定されたチャンネルから即時集計を取得する.

        Parameters
        ----------
        channel : Channel
            即時集計が存在するチャンネル
        allow_read_only : bool, optional
            読み取り専用の即時集計を取得するかどうか, by default False.
            Trueの場合, 自分ではない他のBotの即時集計も取得できる.
        allow_archived : bool, optional
            アーカイブ済みの即時集計を取得するかどうか, by default False.

        Returns
        -------
        Game
            取得した即時集計

        Raises
        ------
        GameNotFound
            即時集計が見つからなかった場合
        """
        after = datetime.now() - timedelta(hours=2)
        async for message in channel.history(limit=None, after=after):

            available = Game.is_valid_message(message, allow_read_only)

            if not available:
                continue

            game = Game.from_message(message)

            if game.is_archived and not allow_archived:
                continue

            return game

        raise GameNotFound

    def to_embed(self) -> Embed:
        """即時集計の情報を埋め込みメッセージとして取得する.

        Returns
        -------
        Embed
            即時集計の情報を埋め込みメッセージとして取得したもの
        """
        title = self.TITLE[self.locale]
        title += f" 6v6\n{self.teams[0]} - {self.teams[1]}"
        race_left = 12 - len(self.races)
        total_scores = self.get_total_scores()

        fmt = format_scores

        embed = Embed(
            title=title,
            description=f"`{fmt(total_scores)} @{race_left}`",
            color=EmbedColor.default,
        )

        for idx, race in enumerate(self.races):
            field_name = f"{idx+1} "

            if race.track is not None:
                field_name += f"- {race.track.get_nick(self.locale)}"

            field_value = f"`{fmt(race.scores)}` | `{race.ranks[0]}`"

            embed.add_field(name=field_name, value=field_value, inline=False)

        if self.penalties != [0, 0]:
            embed.add_field(name="Penalty", value=f"`{fmt(self.penalties, True)}`", inline=False)
        if self.re_picks != [0, 0]:
            embed.add_field(name="Repick", value=f"`{fmt(self.re_picks, True)}`", inline=False)

        if self.banner_users:
            embed.add_field(name="Members", value="> " + ", ".join(map(lambda x: "@" + x, self.banner_users)), inline=False)

        if self.is_archived:
            embed.set_author(name=self.ARCHIVE_TITLE[self.locale])

        return embed

    @staticmethod
    def get_locale(embed: Embed) -> Locale:
        """即時集計の言語を取得する.

        Parameters
        ----------
        embed : Embed
            即時集計の埋め込み

        Returns
        -------
        Locale
            即時集計の言語. 見つからない場合は "ja"
        """
        for locale, title in Game.TITLE.items():
            if embed.title == title:
                return locale

        # ここは通らないはず
        return "ja"

    def get_total_scores(self) -> list[int]:
        """全レースの合計得点を取得する.

        Returns
        -------
        list[int]
            [自チーム, 相手チーム]の合計得点
        """
        scores = [0, 0]

        for r in self.races:
            scores[0] += r.scores[0]
            scores[1] += r.scores[1]

        scores[0] += self.penalties[0] + self.re_picks[0]
        scores[1] += self.penalties[1] + self.re_picks[1]
        return scores

    @staticmethod
    def is_valid_message(message: HybridMessage, allow_read_only: bool = True) -> bool:
        """即時集計のメッセージかどうかを判定する.

        Parameters
        ----------
        message : Message
            判定するメッセージ
        allow_read_only : bool, optional
            読み取り専用のメッセージも許可するかどうか, by default True.
            Trueの場合, 自分のbotのメッセージに加えて, ALLOWED_BOT_IDのメッセージも許可する.
        Returns
        -------
        bool
            即時集計のメッセージかどうか
        """
        bot: Bot = message._state._get_client()  # type: ignore # since _get_client returns self and class Bot is subclass of Client, it is safe to ignore

        if bot.user is None:
            return False

        allowed_ids = [bot.user.id]

        if allow_read_only:
            allowed_ids.append(ALLOWED_BOT_ID)

        return (
            message.author.id in allowed_ids
            and len(message.embeds) > 0
            and isinstance(message.embeds[0].title, str)
            and any(message.embeds[0].title.startswith(t) for t in Game.TITLE.values())
        )

    # TODO: Implement
    def add_race(self, rank_text: str, track_name: str | None = None, race_number: int | None = None) -> None:
        """即時集計にレースを追加する.

        Parameters
        ----------
        rank_text : str
            順位のテキスト
        track_name : str | None
            走ったコースの名前, by default None
        race_number : int | None
            レース番号, by default None.
            Noneの場合, 一番最後のレースとして追加する.
        """
        return

    def remove_race(self, race_number: int) -> None:
        """即時集計からレースを削除する.

        Parameters
        ----------
        race_number : int
            削除するレースの番号
        """
        return
