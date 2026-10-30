from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from discord import ApplicationContext, Embed
from typing_extensions import Required

from mk8dx.lounge.rank import Rank
from utils.parser import get_friend_codes
from utils.utils import get_average

from .errors import NoFriendCodeFound, NoViewablePlayers, TooManyFriendCodes
from .types import BaseHandler as IBaseHandler, FriendHandler as IFriendHandler

__all__ = ("FriendHandler",)

if TYPE_CHECKING:
    from utils.types import HybridContext

    Attr = Literal["mmr", "max_mmr"]

    class Options(TypedDict, total=False):
        embed: Required[Embed]
        content: str


MAX_FRIEND_CODES = 24


class FriendHandler(IBaseHandler, IFriendHandler):
    async def friend_mmr(
        self,
        ctx: HybridContext,
        *,
        text: str,
        ascending: bool | None = None,
        view_original: bool = True,
    ) -> None:
        return await self._friend_mmr(
            ctx,
            attribute="mmr",
            text=text,
            ascending=ascending,
            view_original=view_original,
        )

    async def friend_peak_mmr(
        self,
        ctx: HybridContext,
        *,
        text: str,
        ascending: bool | None = None,
        view_original: bool = True,
    ) -> None:
        return await self._friend_mmr(
            ctx,
            attribute="max_mmr",
            text=text,
            ascending=ascending,
            view_original=view_original,
        )

    async def _friend_mmr(
        self,
        ctx: HybridContext,
        *,
        attribute: Attr,
        text: str,
        ascending: bool | None = None,
        view_original: bool = True,
    ) -> None:
        """textからフレンドコードを抽出し, プレイヤーの平均MMRを表示する.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        attribute : Literal[&quot;mmr&quot;, &quot;max_mmr&quot;]
            参照する項目. &quot;mmr&quot; または &quot;max_mmr&quot;.
        text : str
            MMRを含むテキスト.
        ascending : bool | None, optional
            昇順にするかどうか. Falseなら降順, Noneの場合はもとの並び順, by default None
        view_original : bool, optional
            力されたテキストを出力と合わせて表示するかどうか, by default True
        """

        friend_codes = get_friend_codes(text)

        if not friend_codes:
            raise NoFriendCodeFound

        if len(friend_codes) > MAX_FRIEND_CODES:
            raise TooManyFriendCodes

        is_app_ctx = isinstance(ctx, ApplicationContext)

        if is_app_ctx:
            await ctx.response.defer()  # type: ignore

        data = await self.get_players_by_friend_codes(friend_codes)

        average = get_average([player for _, player in data], lambda p: getattr(p, attribute, None))

        if average is None:
            raise NoViewablePlayers

        rank = Rank.from_mmr(mmr=average)

        display_names: dict[Attr, str] = {
            "mmr": "MMR",
            "max_mmr": "Peak MMR",
        }
        title = f"Average {display_names[attribute]}: {average:.1f}"

        embed = rank.to_embed()
        embed.title = title

        lines: list[str] = []

        if ascending is not None:
            valid = []
            invalid = []

            for v in data:
                if getattr(v[1], attribute, None) is None:
                    invalid.append(v)
                else:
                    valid.append(v)

            sorted_data = sorted(valid, key=lambda v: getattr(v[1], attribute), reverse=not ascending) + invalid
        else:
            sorted_data = data

        for idx, (code, player) in enumerate(sorted_data):
            line = f"{idx + 1}. "
            value: int | None = getattr(player, attribute, None)

            if player is not None and value is not None:
                line += f"[{player.name}]({player.mkc_url}) ({value})"
            else:
                line += f"N/A ({code})"

            lines.append(line)

        lines.append(f"\n**Rank**: {rank.name}")
        embed.description = "\n".join(lines)

        options: Options = {"embed": embed}

        if is_app_ctx and view_original:
            options["content"] = text

        if is_app_ctx:
            await ctx.respond(**options)  # type: ignore
        else:
            await ctx.send(**options)
