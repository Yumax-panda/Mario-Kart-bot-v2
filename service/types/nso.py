from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TypedDict

__all__ = (
    "Version",
    "AccessToken",
    "UserInfo",
    "FToken",
    "NSOToken",
    "SwitchAccount",
    "NintendoSwitchOnlineService",
)


class Version(TypedDict):
    nso_version: str


class AccessToken(TypedDict):
    id_token: str
    access_token: str


class UserInfo(TypedDict):
    language: str
    country: str
    birthday: str


class FToken(TypedDict):
    f: str
    timestamp: str
    request_id: str


class NSOToken(TypedDict):
    token: str
    expires_in: int


class SwitchAccount(TypedDict):
    id: str
    nsa_id: str
    image_uri: str
    name: str
    extras: dict


class NintendoSwitchOnlineService(metaclass=ABCMeta):

    @property
    @abstractmethod
    def nso_product_version(self) -> str:
        """Nintendo Switch Onlineのプロダクトバージョンを返す.

        Returns
        -------
        str
            プロダクトバージョン
        """
        ...

    @abstractmethod
    async def get_version(self) -> Version:
        """Nintendo Switch Onlineのバージョン情報を取得する. get_nso_tokenでエラーが発生した場合に, このバージョンを確認すること.

        Returns
        -------
        Version
            バージョン情報

        Raises
        ------
        BotError
            バージョン情報の取得に失敗した場合
        """
        ...

    @abstractmethod
    async def get_session_token(self, session_token_code: str, verifier: str) -> str:
        """セッショントークンを取得する. セッショントークンはアクセストークンを取得するために必要.

        Parameters
        ----------
        session_token_code : str
            セッショントークンコード
        verifier : str
            認証コード

        Returns
        -------
        str
            セッショントークン

        Raises
        ------
        BotError
            セッショントークンの取得に失敗した場合
        """
        ...

    @abstractmethod
    async def get_access_token(self, session_token: str) -> AccessToken:
        """Nintendo Switch Onlineのアクセストークンを取得する.

        Parameters
        ----------
        session_token : str
            セッショントークン

        Returns
        -------
        AccessToken
            アクセストークン

        Raises
        ------
        BotError
            アクセストークンの取得に失敗した場合
        """
        ...

    @abstractmethod
    async def get_user_info(self, access_token: str) -> UserInfo:
        """Nintendo Switch Onlineに登録されたユーザー情報を取得する.

        Parameters
        ----------
        access_token : str
            アクセストークン

        Returns
        -------
        UserInfo
            ユーザー情報

        Raises
        ------
        BotError
            ユーザー情報の取得に失敗した場合
        """
        ...

    @abstractmethod
    async def get_f(self, id_token: str) -> FToken:
        """Fトークンを取得する.
        ref: https://github.com/imink-app/f-API

        Parameters
        ----------
        id_token : str
            アクセストークンに付随するIDトークン

        Returns
        -------
        FToken
            Fトークン

        Raises
        ------
        BotError
            Fトークンの取得に失敗した場合
        """
        ...

    @abstractmethod
    async def get_nso_token(self, access_token: AccessToken) -> NSOToken:
        """Nintendo Switch OnlineへログインしてNSOトークンを取得する.

        Parameters
        ----------
        access_token : AccessToken
            アクセストークン

        Returns
        -------
        NSOToken
            NSOトークン

        Raises
        ------
        BotError
            NSOトークンの取得に失敗した場合
        """
        ...

    @abstractmethod
    async def get_switch_account(self, friend_code: str, nso_token: str) -> SwitchAccount:
        """Nintendo Switch Onlineに登録されたアカウント情報を取得する.

        Parameters
        ----------
        friend_code : str
            検索するフレンドコード
        nso_token : str
            NSOトークン

        Returns
        -------
        SwitchAccount
            アカウント情報

        Raises
        ------
        BotError
            アカウント情報の取得に失敗した場合
        """
        ...

    @abstractmethod
    async def create_friend_request(self, target_nsa_id: str, nso_token: str) -> None:
        """指定したNintendo Switch Accountにフレンドリクエストを送信する.

        Parameters
        ----------
        target_nsa_id : str
            フレンドリクエストを送信する対象のNintendo Switch Account ID
        nso_token : str
            送信者のNintendo Switch Onlineトークン

        Raises
        ------
        BotError
            フレンドリクエストの送信に失敗した場合
        """
        ...
