from __future__ import annotations

import asyncio
import random
from copy import deepcopy
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Final,
    Iterable,
    ParamSpec,
    Sequence,
    TypedDict,
    TypeVar,
)

from discord import ApplicationContext, Embed, Forbidden, Member, Role
from discord.utils import get

from utils.constants import MAX_EMBED_FIELDS, MAX_ROLES, EmbedColor
from utils.format import user_mention
from utils.parser import get_hours as _get_hours

from .errors import (
    BotMissingPermissions,
    FailedToGetBotData,
    FailedToGetMemberData,
    GuildNotFound,
    NoMembersAvailable,
    NotGathering,
    TimeNotSelected,
    TimeOutOfRange,
    TooManyRoles,
    TooManyTimeSelected,
)
from .types import BaseHandler as IBaseHandler, RecruitHandler as IRecruitHandler

__all__ = ("RecruitHandler",)

if TYPE_CHECKING:
    from discord import Guild, Message, Role

    from model.gathers import ParticipationType
    from utils.types import HybridContext, HybridMember

    class ParticipatePayload(TypedDict, total=False):
        embed: Embed
        content: str

    class GatherData(TypedDict):
        type: ParticipationType
        user_id: int
        hour: int

    State = dict[int, dict[ParticipationType, list[int]]]

else:
    ParticipatePayload = dict
    GatherData = dict

P = ParamSpec("P")
T = TypeVar("T")

EMBED_TITLE: Final[str] = "**6v6 War List**"
ARCHIVE: Final[str] = "Archive"
ALLOWED_PARTICIPATION_HOUR_MIN: Final[int] = 0
ALLOWED_PARTICIPATION_HOUR_MAX: Final[int] = 48


# NOTE: ハンドラの処理で型安全にするため, ctx.guildがNoneの場合は例外を投げるようにしているが,
# cog_checkでguildがNoneではないことを確認しているため, 実際には発生しない.
class RecruitHandler(IBaseHandler, IRecruitHandler):

    async def can(self, ctx: HybridContext, members: Sequence[HybridMember], target: str) -> None:
        return await self._participate(ctx, "c", members, target)

    async def tentative(self, ctx: HybridContext, members: Sequence[HybridMember], target: str) -> None:
        return await self._participate(ctx, "t", members, target)

    async def substitute(self, ctx: HybridContext, members: Sequence[HybridMember], target: str) -> None:
        return await self._participate(ctx, "s", members, target)

    async def drop(self, ctx: HybridContext, members: Sequence[HybridMember], target: str) -> None:
        if isinstance(ctx, ApplicationContext):
            await ctx.defer()

        guild: Guild | None = ctx.guild

        if guild is None:
            raise GuildNotFound

        if not all(isinstance(m, Member) for m in members):
            raise FailedToGetMemberData

        member_ids = {m.id for m in members}
        hours = get_hours(target)

        await self.repo.delete_gathers(guild.id, member_ids, hours)
        await remove_roles(guild, members, hours)  # type: ignore # memberはMember型のリストなので問題ない

        data = await self.repo.get_all_gathers(guild.id)
        state = get_gather_state(data)
        synced = sync_state(state, guild.roles)
        embed = create_recruit_embed(synced)

        await self._refresh(ctx, embed=embed)

    async def clear(self, ctx: HybridContext) -> None:
        if isinstance(ctx, ApplicationContext):
            await ctx.defer()

        guild: Guild | None = ctx.guild  # type: ignore

        if guild is None:
            raise GuildNotFound

        guild_id: int = ctx.guild.id  # type: ignore

        roles = [
            role
            for role in guild.roles
            if role.name.isdigit() and ALLOWED_PARTICIPATION_HOUR_MIN <= int(role.name) <= ALLOWED_PARTICIPATION_HOUR_MAX
        ]

        if roles:
            await asyncio.gather(*[role.delete() for role in roles])

        await self.repo.clear_gathers(guild_id)

        content = "挙手情報を削除しました."
        prev = await self._fetch_previous_message(ctx)

        if prev:
            await prev.edit(embed=to_archive(prev.embeds[0]))  # embeds[0]は_fetch_previous_messageで存在が保証されている

        if isinstance(ctx, ApplicationContext):
            await ctx.respond(content=content)
        else:
            await ctx.send(content=content)

    async def out(self, ctx: HybridContext, target: str) -> None:
        if isinstance(ctx, ApplicationContext):
            await ctx.defer()

        guild: Guild | None = ctx.guild

        if guild is None:
            raise GuildNotFound

        guild_id: int = guild.id
        hours = get_hours(target)

        await self.repo.delete_all_gathers_by_hours(guild_id, hours)

        await delete_roles(guild, hours)

        deleted = ", ".join(map(str, hours))
        content = f"募集を削除しました. ({deleted})"

        data = await self.repo.get_all_gathers(guild_id)
        state = get_gather_state(data)
        synced = sync_state(state, guild.roles)
        embed = create_recruit_embed(synced)

        await self._refresh(ctx, embed=embed, content=content)

    async def now(self, ctx: HybridContext) -> None:
        if isinstance(ctx, ApplicationContext):
            await ctx.defer()

        guild: Guild | None = ctx.guild

        if guild is None:
            raise GuildNotFound

        data = await self.repo.get_all_gathers(guild.id)
        state = get_gather_state(data)
        synced = sync_state(state, guild.roles)

        if not synced:
            raise NotGathering

        embed = create_recruit_embed(synced)

        await self._refresh(ctx, embed=embed)

    async def pick(self, ctx: HybridContext, role: Role) -> None:
        if isinstance(ctx, ApplicationContext):
            await ctx.defer()

        members = role.members

        if not members:
            raise NoMembersAvailable

        member = random.choice(members)
        mention = member.mention

        if isinstance(ctx, ApplicationContext):
            await ctx.respond(content=mention)
        else:
            await ctx.send(content=mention)

    async def _participate(
        self,
        ctx: HybridContext,
        type: ParticipationType,
        members: Sequence[HybridMember],
        target: str,
    ) -> None:
        """指定した形式で挙手する.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        type : ParticipationType
            参加タイプ.
        members : Sequence[HybridMember]
            参加するメンバー.
        target : str
            挙手する時間.
            例えば, `19, 20`や`20-24`のような形式.
        """
        if isinstance(ctx, ApplicationContext):
            await ctx.defer()

        guild: Guild | None = ctx.guild

        if guild is None:
            raise GuildNotFound

        if not all(isinstance(m, Member) for m in members):
            raise FailedToGetMemberData

        member_ids = {m.id for m in members}
        hours = get_hours(target)

        await add_roles(guild, members, hours)  # type: ignore # memberはMember型のリストなので問題ない

        await self.repo.delete_gathers(
            guild_id=guild.id,
            user_ids=member_ids,
            hours=hours,
        )
        await self.repo.insert_gathers(
            guild_id=guild.id,
            user_ids=member_ids,
            type=type,
            hours=hours,
        )

        data = await self.repo.get_all_gathers(guild.id)
        state = get_gather_state(data)
        synced = sync_state(state, guild.roles)
        embed = create_recruit_embed(synced)

        payload: ParticipatePayload = {
            "embed": embed,
        }

        filled: list[int] = []

        for hour in sorted(synced.keys()):
            is_filled = len(synced[hour].get("c", [])) >= 6

            # 挙手した時間で6人以上そろっている時間がある場合, メンバーへメンションする.
            if is_filled and hour in hours:
                filled.append(hour)

        if filled:
            content = ""
            for hour in filled:
                content += f'**{hour}** {", ".join(map(user_mention, synced[hour]["c"]))}\n'

            payload["content"] = content

        await self._refresh(ctx, **payload)

    async def _fetch_previous_message(self, ctx: HybridContext) -> Message | None:
        """以前に送信されていた挙手情報のEmbedを含んだメッセージを取得する.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.

        Returns
        -------
        Message | None
            以前に送信されていた挙手情報のEmbedを含んだメッセージ.
        """
        client = ctx.bot.user

        if client is None:
            raise FailedToGetBotData

        bot_id = client.id

        async for message in ctx.channel.history(limit=20, oldest_first=False):
            is_prev_embed = message.author.id == bot_id and message.embeds and not is_archived(message.embeds[0])

            if is_prev_embed:
                return message

        return None

    async def _refresh(self, ctx: HybridContext, *, embed: Embed, content: str | None = None) -> None:
        """以前に送信されていた挙手情報のEmbedを含んだメッセージを削除し, 新たに送信する.
        メッセージが見つからない場合は新たに送信する.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        embed : Embed
            送信するEmbed.
        content : str | None, optional
            送信する内容.
        """
        prev = await self._fetch_previous_message(ctx)

        if prev:
            await prev.delete()

        payload: ParticipatePayload = {
            "embed": embed,
        }

        if content:
            payload["content"] = content

        if isinstance(ctx, ApplicationContext):
            await ctx.respond(**payload)
        else:
            await ctx.send(**payload)


def get_hours(text: str) -> list[int]:
    """utils.parser.get_hoursの処理をした後に, 入力が正しいかを確認する.

    Raises
    ------
    TimeOutOfRange
        時間が0から48の範囲外の場合
    TimeNotSelected
        時間が選択されていない場合
    """
    hours = _get_hours(text)

    if not hours:
        raise TimeNotSelected

    if not all(ALLOWED_PARTICIPATION_HOUR_MIN <= hour <= ALLOWED_PARTICIPATION_HOUR_MAX for hour in hours):
        raise TimeOutOfRange

    return hours


def maybe_forbidden(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    """権限に関するエラーでタスクが失敗したときのエラーメッセージを送るためのデコレータ.

    Parameters
    ----------
    func : Callable[P, Awaitable[T]]
        discordサーバーの権限に関するエラーによって失敗しうるコルーチン.

    Returns
    -------
    Callable[P, Awaitable[T]]
        ラップされた関数.

    Raises
    ------
    BotError
        `discord.Forbidden`が発生したとき。
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return await func(*args, **kwargs)
        except Forbidden as e:
            raise BotMissingPermissions from e

    return wrapper


@maybe_forbidden
async def add_roles(guild: Guild, member: Iterable[Member], hours: Iterable[int]) -> None:
    """指定した時間の役職を付与する.

    Parameters
    ----------
    guild : Guild
        ギルド.
    member : Iterable[Member]
        役職を付与するメンバー.
    hours : Iterable[int]
        役職を付与する時間.
    """
    roles: list[Role] = []
    create_role_tasks: list[Coroutine[Any, Any, Role]] = []

    for hour in hours:
        role_name = str(hour)
        if (role := get(guild.roles, name=role_name)) is None:
            task = guild.create_role(name=role_name, mentionable=True)
            create_role_tasks.append(task)
        else:
            roles.append(role)

    ensure_is_under_max_roles_count(hours, guild.roles)

    if create_role_tasks:
        roles.extend(await asyncio.gather(*create_role_tasks))

    add_role_tasks = [member.add_roles(*roles) for member in member]
    await asyncio.gather(*add_role_tasks)


@maybe_forbidden
async def remove_roles(guild: Guild, member: Iterable[Member], hours: Iterable[int]) -> None:
    """指定した時間の役職を剥奪する.

    Parameters
    ----------
    guild : Guild
        ギルド.
    member : Iterable[Member]
        役職を削除するメンバー.
    hours : Iterable[int]
        役職を削除する時間.
    """
    roles: list[Role] = []
    for hour in hours:
        role_name = str(hour)
        if (role := get(guild.roles, name=role_name)) is not None:
            roles.append(role)
    remove_role_tasks = [member.remove_roles(*roles) for member in member]
    await asyncio.gather(*remove_role_tasks)


@maybe_forbidden
async def delete_roles(guild: Guild, hours: Iterable[int]) -> None:
    """指定した時間の役職を削除する.

    Parameters
    ----------
    guild : Guild
        ギルド.
    hours : Iterable[int]
        削除する時間.
    """
    roles: list[Role] = []
    for hour in hours:
        role_name = str(hour)
        if (role := get(guild.roles, name=role_name)) is not None:
            roles.append(role)
    remove_role_tasks = [role.delete() for role in roles]
    await asyncio.gather(*remove_role_tasks)


# TODO: test
def get_gather_state(data: Iterable[GatherData]) -> State:
    """DBから取得した挙手情報のデータを整形し、挙手状況を得る.

    Parameters
    ----------
    data : Iterable[GatherData]
        挙手情報.

    Returns
    -------
    State
        整形した挙手情報. keyは時間.
    """
    d: State = {}

    for item in data:
        d.setdefault(item["hour"], {}).setdefault(item["type"], []).append(item["user_id"])

    return d


def create_recruit_embed(data: State) -> Embed:
    """挙手状況を表示するEmbedを作成する.

    Parameters
    ----------
    data : State
        挙手情報.

    Returns
    -------
    Embed
        作成したEmbed.
    """

    e = Embed(title=EMBED_TITLE, color=EmbedColor.default)

    for hour in sorted(data.keys()):
        is_empty = sum(len(v) for v in data[hour].values()) == 0

        if is_empty:
            e.add_field(name=f"{hour}@6", value="> なし", inline=False)
            continue

        c = data[hour].get("c", [])
        t = data[hour].get("t", [])
        s = data[hour].get("s", [])

        name = f"{hour}@{6-len(c)}"
        value = f'> {", ".join(map(user_mention, c))}'

        if (submembers_count := len(t) + len(s)) > 0:
            name += f" ({submembers_count})"
            _submember_mentions: list[str] = []
            if len(s) > 0:
                _submember_mentions.extend(map(lambda i: f"補{user_mention(i)}", s))
            if len(t) > 0:
                _submember_mentions.extend(map(lambda i: f"仮{user_mention(i)}", t))
            value += f'({", ".join(_submember_mentions)})'

        e.add_field(name=name, value=value, inline=False)
        e.set_footer(text="補欠: Substitute, 仮: Tentative")

    return e


def to_archive(embed: Embed) -> Embed:
    """Embedをアーカイブ用に変換する.

    Parameters
    ----------
    embed : Embed
        変換するEmbed.

    Returns
    -------
    Embed
        変換したEmbed.
    """
    e = embed.copy()
    e.colour = EmbedColor.archive
    e.set_author(name=ARCHIVE)

    return e


def is_archived(embed: Embed) -> bool:
    """Embedがアーカイブ用かどうかを判定する.

    Parameters
    ----------
    embed : Embed
        判定するEmbed.

    Returns
    -------
    bool
        アーカイブ用のEmbedならTrue.
    """
    return embed.colour == EmbedColor.archive and embed.author is not None and embed.author.name == "Archive"


# TODO: test
def sync_state(stored_state: State, guild_roles: Iterable[Role]) -> State:
    """挙手情報の状態をサーバーと同期する.

    募集時間を表すロールが存在しているが、挙手していない時間がある場合、その時間の挙手情報を追加する.

    Parameters
    ----------
    stored_state : State
        DBから取得した挙手情報.
    guild_roles : Iterable[Role]
        サーバーのロール.

    Returns
    -------
    State
        同期後の挙手情報.
    """
    new_state = deepcopy(stored_state)

    gathering_times = [
        int(role.name)
        for role in guild_roles
        if role.name.isdigit() and ALLOWED_PARTICIPATION_HOUR_MIN <= int(role.name) <= ALLOWED_PARTICIPATION_HOUR_MAX
    ]

    for hour in gathering_times:
        if hour not in new_state:
            new_state[hour] = {"c": [], "t": [], "s": []}

    return new_state


def ensure_is_under_max_roles_count(hours: Iterable[int], guild_roles: Iterable[Role]) -> bool:
    """挙手する時間の数が上限を超えていないかを確認する.

    Parameters
    ----------
    hours : Iterable[int]
        挙手する時間.
    guild_roles : Iterable[Role]
        サーバーのロール.

    Returns
    -------
    bool
        挙手する時間の数が上限を超えていない場合True.

    Raises
    ------
    TooManyTimeSelected
        挙手する時間が多すぎる場合.
    TooManyRoles
        ロールがサーバーの上限を超えている場合.
    """
    gathering_hours = {
        role.name
        for role in guild_roles
        if role.name.isdigit() and ALLOWED_PARTICIPATION_HOUR_MIN <= int(role.name) <= ALLOWED_PARTICIPATION_HOUR_MAX
    } | set(map(str, hours))

    if len(gathering_hours) > MAX_EMBED_FIELDS:
        raise TooManyTimeSelected

    all_role_names = {role.name for role in guild_roles} | gathering_hours

    if len(all_role_names) > MAX_ROLES:
        raise TooManyRoles

    return True
