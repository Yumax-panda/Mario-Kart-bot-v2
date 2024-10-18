from __future__ import annotations

import re
from typing import TYPE_CHECKING

from discord import ButtonStyle, InputTextStyle
from discord.ui import Button, InputText

from .core import Modal, View
from .errors import FailedToGetUserData, InvalidAuthURI, InvalidTextInput, MessageNotFound, NintendoSwitchAccountIDNotFound
from .utils import DeleteButton

__all__ = (
    "LoginView",
    "LoginButton",
    "LoginModal",
)

if TYPE_CHECKING:
    from discord import Interaction

    from bot import Bot


class LoginView(View):

    def __init__(self, verifier: str) -> None:
        button = LoginButton(verifier=verifier)
        super().__init__(button, timeout=180.0, disable_on_timeout=True)


class LoginButton(Button):

    def __init__(self, verifier: str) -> None:
        super().__init__(label="Next", custom_id=verifier)

    async def callback(self, interaction: Interaction) -> None:
        verifier = self.custom_id

        if verifier is None:
            raise MessageNotFound

        await interaction.response.send_modal(LoginModal(verifier=verifier))


class LoginModal(Modal):

    def __init__(self, verifier: str) -> None:
        super().__init__(
            InputText(
                style=InputTextStyle.short,
                custom_id="auth_uri",
                placeholder="npf71b963c1b7b6d119://auth#...",
                required=True,
                label="Login URL",
            ),
            custom_id=verifier,
            title="Login",
            timeout=180.0,
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()

        auth_uri = self.children[0].value

        if auth_uri is None:
            raise InvalidTextInput

        session_token_code = get_session_token_code(auth_uri)
        verifier = self.custom_id

        bot: Bot = interaction.client  # type: ignore
        session_token = await bot.h.srv.get_session_token(session_token_code, verifier)

        if (user := interaction.user) is None:
            raise FailedToGetUserData

        await bot.h.repo.put_session_token(user_id=user.id, session_token=session_token)
        access_token = await bot.h.srv.get_access_token(session_token)
        nso_token = await bot.h.srv.get_nso_token(access_token)
        await bot.h.repo.put_nso_token(user_id=user.id, nso_token=nso_token["token"], expires_in=nso_token["expires_in"])

        await interaction.respond("ログインしました.")


_SESSION_TOKEN_CODE_RE = re.compile(r"session_token_code=([A-Za-z0-9-._]+)")


# TODO: test
def get_session_token_code(auth_uri: str) -> str:
    """認証URIからセッショントークンコードを取得する.

    Parameters
    ----------
    auth_uri : str
        認証URI

    Returns
    -------
    str
        セッショントークンコード

    Raises
    ------
    InvalidAuthURI
        認証URIが無効な場合
    """

    match = _SESSION_TOKEN_CODE_RE.search(auth_uri)
    if match is None:
        raise InvalidAuthURI

    return match.group(1)


class SingleFriendRequestView(View):

    def __init__(self, nsa_id: str, ephemeral: bool):
        super().__init__(
            SingleFriendRequestButton(nsa_id=nsa_id),
            timeout=180.0,
            disable_on_timeout=True,
        )

        if not ephemeral:
            self.add_item(DeleteButton(label="終了"))


class SingleFriendRequestButton(Button):

    def __init__(self, nsa_id: str):
        """フレンド申請ボタンを作成する.

        Parameters
        ----------
        nsa_id : str
            フレンド申請を送る相手のNintendo Switch Online ID.
        """
        super().__init__(
            style=ButtonStyle.secondary,
            label="申請",
            custom_id=nsa_id,
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()

        bot: Bot = interaction.client  # type: ignore

        target_nsa_id = self.custom_id

        if not target_nsa_id:
            raise NintendoSwitchAccountIDNotFound

        user = interaction.user

        if not user or not user.id:
            raise FailedToGetUserData

        nso_token = await bot.h.repo.get_nso_token(user_id=user.id)

        if not nso_token:
            raise FailedToGetUserData

        await bot.h.srv.create_friend_request(target_nsa_id, nso_token)
        await interaction.followup.send("フレンド申請を送信しました.")
