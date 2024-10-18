from __future__ import annotations

import asyncio
import base64
import hashlib
import random
import secrets
import string
from typing import TYPE_CHECKING, Literal, TypedDict

from discord import ApplicationContext, Embed
from typing_extensions import Required

from mk8dx.lounge.rank import Rank
from ui.friend import LoginView, SingleFriendRequestView
from utils.constants import EmbedColor
from utils.parser import get_friend_codes, maybe_param
from utils.utils import get_average

from .errors import LoginRequired, NoFriendCodeFound, NoViewablePlayers, TooManyFriendCodes
from .types import BaseHandler as IBaseHandler, FriendHandler as IFriendHandler

__all__ = ("FriendHandler",)

if TYPE_CHECKING:
    from model.requests import RequestPayload
    from utils.types import Context, HybridContext

    Attr = Literal["mmr", "max_mmr"]

    class Options(TypedDict, total=False):
        embed: Required[Embed]
        content: str


MAX_FRIEND_CODES = 24
MAX_FRIEND_REQUESTS = 12


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

    async def friend_setup(self, ctx: ApplicationContext) -> None:
        await ctx.response.defer(ephemeral=True)

        verifier = create_verifier()
        url = create_login_url(verifier)

        embed = Embed(
            title="Login",
            description=f"[こちら]({url})をクリックし、ログインをした後に「この人にする」のリンク先をコピペしてください。",
            color=EmbedColor.default,
        )

        view = LoginView(verifier=verifier)

        await ctx.respond(embed=embed, view=view, ephemeral=True)

    async def friend_request(self, ctx: ApplicationContext, code: str, private: bool) -> None:
        await ctx.response.defer(ephemeral=private)
        embed, view = await self._get_friend_request_components(ctx.author.id, code, ephemeral=private)
        await ctx.respond(embed=embed, view=view, ephemeral=private)

    async def text_friend_request(self, ctx: Context, *, code: str) -> None:
        embed, view = await self._get_friend_request_components(ctx.author.id, code, ephemeral=False)
        await ctx.send(embed=embed, view=view)

    async def friend_code(self, ctx: ApplicationContext, private: bool) -> None:
        user_id = ctx.user.id
        linked_id = await self.repo.get_lounge_id(user_id)
        await self.friend_request(ctx, str(linked_id or user_id), private)

    async def friend_multiple(self, ctx: ApplicationContext, codes: str, private: bool) -> None:
        await ctx.response.defer(ephemeral=private)

        parsed_friend_codes = get_friend_codes(codes)

        if not parsed_friend_codes:
            raise NoFriendCodeFound

        if len(parsed_friend_codes) > MAX_FRIEND_REQUESTS:
            raise TooManyFriendCodes

        nso_token = await self._get_nso_token_by_discord_id(ctx.author.id)

        switch_accounts: RequestPayload = []

        for code in parsed_friend_codes:
            try:
                switch_account = await self.srv.get_switch_account(code, nso_token)
                switch_accounts.append(
                    {
                        "nsa_id": switch_account["nsa_id"],
                        "name": switch_account["name"],
                        "fc": code,
                    }
                )
            except:
                pass
            finally:
                # フレンド申請APIのレートリミット回避
                await asyncio.sleep(5)

        if not switch_accounts:
            raise NoFriendCodeFound

        await self.repo.put_requests(ctx.author.id, switch_accounts)

    async def _get_friend_request_components(
        self, user_id: int | str, code: str, ephemeral: bool
    ) -> tuple[Embed, SingleFriendRequestView]:
        """フレンド申請に必要なコンポーネントを取得する.

        Parameters
        ----------
        user_id : int | str
            フレンド申請をするユーザーのdiscord ID.
        code : str
            フレンド申請をする相手のフレンドコード.
        ephemeral : bool
            メッセージを一時的にするかどうか.

        Returns
        -------
        tuple[Embed, SingleFriendRequestView]
            フレンド申請に必要なEmbedとView.

        Raises
        ------
        NoFriendCodeFound
            フレンドコードやプレイヤーが見つからなかった場合.

        """
        param = maybe_param(code)
        friend_code: str | None = param.get("fc")  # type: ignore

        if not friend_code:
            player = await self.lc.get_player(**param)

            if not player or not player.switch_fc:
                raise NoFriendCodeFound

            friend_code = player.switch_fc

        nso_token = await self._get_nso_token_by_discord_id(user_id)
        switch_account = await self.srv.get_switch_account(friend_code, nso_token)

        view = SingleFriendRequestView(nsa_id=switch_account["nsa_id"], ephemeral=ephemeral)
        embed = Embed(color=EmbedColor.default, title=switch_account["name"], description=f"`{friend_code}`")
        embed.set_author(name="フレンド申請", icon_url=switch_account["image_uri"])

        return embed, view

    async def _get_nso_token_by_discord_id(self, discord_id: int | str) -> str:
        """discord_idからNintendo Switch Onlineのトークンを取得する.

        Parameters
        ----------
        discord_id : int | str
            DiscordのユーザーID.

        Returns
        -------
        str
            Nintendo Switch Onlineのトークン.

        Raises
        ------
        LoginRequired
            まだログインしていない場合.
        """
        stored_token = await self.repo.get_nso_token(int(discord_id))

        if stored_token:
            return stored_token

        stored_session_token = await self.repo.get_session_token(int(discord_id))

        if not stored_session_token:
            raise LoginRequired

        access_token = await self.srv.get_access_token(stored_session_token)
        nso_token_payload = await self.srv.get_nso_token(access_token)

        nso_token = nso_token_payload["token"]
        expires_in = nso_token_payload["expires_in"]

        await self.repo.put_nso_token(int(discord_id), nso_token, expires_in)

        return nso_token


def create_verifier() -> str:
    """認証コードを生成する.

    Returns
    -------
    str
        認証コード
    """
    verifier = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(verifier).decode("utf-8").replace("=", "")


def create_login_url(verifier: str) -> str:
    """ログインURLを生成する.

    Parameters
    ----------
    verifier : str
        認証コード

    Returns
    -------
    str
        ログインURL
    """
    sha256 = hashlib.sha256()
    sha256.update(verifier.encode("utf-8"))

    state = "".join(random.choices(string.ascii_letters, k=50))
    challenge = base64.urlsafe_b64encode(sha256.digest()).decode("utf-8").replace("=", "")

    return f"https://accounts.nintendo.com/connect/1.0.0/authorize?state={state}&redirect_uri=npf71b963c1b7b6d119://auth&client_id=71b963c1b7b6d119&scope=openid%20user%20user.birthday%20user.mii%20user.screenName&response_type=session_token_code&session_token_code_challenge={challenge}&session_token_code_challenge_method=S256&theme=login_form"
