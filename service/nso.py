from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Final

from aiohttp import ClientSession

from service.types.nso import Version

from .errors import (
    FailedToGetAccessToken,
    FailedToGetFToken,
    FailedToGetNintendoSwitchAccount,
    FailedToGetSessionToken,
    FailedToGetUserInfo,
    FailedToGetVersion,
    FailedToLogin,
    FailedToSendFriendRequest,
)
from .types.nso import NintendoSwitchOnlineService as INintendoSwitchOnlineService

__all__ = ("NintendoSwitchOnlineService",)

if TYPE_CHECKING:
    from .types import AccessToken, FToken, NSOToken, SwitchAccount, UserInfo, Version

NINTENDO_CLIENT_ID: Final[str] = "71b963c1b7b6d119"
PRODUCT_VERSION: Final[str] = "2.10.1"


class NintendoSwitchOnlineService(INintendoSwitchOnlineService):

    __new_version_cache: Version

    def __init__(self):
        pass

    @property
    def nso_product_version(self) -> str:
        if hasattr(self, "__new_version_cache"):
            return self.__new_version_cache["nso_version"]

        return PRODUCT_VERSION

    async def get_version(self) -> Version:
        async with ClientSession() as session:
            async with session.get("https://api.imink.app/config") as response:
                if response.status != 200:
                    raise FailedToGetVersion
                data = await response.json()
                return {"nso_version": data["nso_version"]}

    async def get_session_token(self, session_token_code: str, verifier: str) -> str:
        async with ClientSession() as session:
            async with session.post(
                "https://accounts.nintendo.com/connect/1.0.0/api/session_token",
                data={
                    "client_id": NINTENDO_CLIENT_ID,
                    "session_token_code": session_token_code,
                    "session_token_code_verifier": verifier,
                },
            ) as resp:
                if resp.status != 200:
                    raise FailedToGetSessionToken
                data = await resp.json()
                return data["session_token"]

    async def get_access_token(self, session_token: str) -> AccessToken:
        async with ClientSession() as session:
            async with session.post(
                "https://accounts.nintendo.com/connect/1.0.0/api/token",
                data={
                    "client_id": NINTENDO_CLIENT_ID,
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token",
                    "session_token": session_token,
                },
            ) as resp:
                if resp.status != 200:
                    raise FailedToGetAccessToken
                data = await resp.json()
                return {
                    "access_token": data["access_token"],
                    "id_token": data["id_token"],
                }

    async def get_user_info(self, access_token: str) -> UserInfo:
        async with ClientSession() as session:
            async with session.get(
                "https://api.accounts.nintendo.com/2.0.0/users/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
            ) as resp:
                if resp.status != 200:
                    raise FailedToGetUserInfo
                data = await resp.json()
                return {
                    "birthday": data["birthday"],
                    "country": data["country"],
                    "language": data["language"],
                }

    async def get_f(self, id_token: str) -> FToken:
        async with ClientSession() as session:
            async with session.post("https://api.imink.app/f", json={"token": id_token, "hash_method": 1}) as response:
                if response.status != 200:
                    raise FailedToGetFToken
                data = await response.json()
                return {
                    "f": data["f"],
                    "timestamp": data["timestamp"],
                    "request_id": data["request_id"],
                }

    async def get_nso_token(self, access_token: AccessToken) -> NSOToken:
        [f, user_info] = await asyncio.gather(
            self.get_f(access_token["id_token"]),
            self.get_user_info(access_token["access_token"]),
        )

        async def fetch(product_version: str) -> NSOToken:
            async with ClientSession() as session:
                async with session.post(
                    "https://api-lp1.znc.srv.nintendo.net/v3/Account/Login",
                    json={
                        "parameter": {
                            "naIdToken": access_token["id_token"],
                            "timestamp": str(f["timestamp"]),
                            "requestId": f["request_id"],
                            "f": f["f"],
                            "language": user_info["language"],
                            "naCountry": user_info["country"],
                            "naBirthday": user_info["birthday"],
                        }
                    },
                    headers={
                        "Content-Type": "application/json; charset=utf-8",
                        "User-Agent": "com.nintendo.znca/2.2.0 (Android/10)",
                        "X-ProductVersion": product_version,
                        "X-Platform": "Android",
                    },
                ) as response:
                    if response.status != 200:
                        raise FailedToLogin
                    data = await response.json()
                    # NOTE: バージョンが違うと, resultキーが存在しない
                    cred = data["result"]["webApiServerCredential"]
                    return {
                        "expires_in": cred["expiresIn"],
                        "token": cred["accessToken"],
                    }

        try:
            return await fetch(self.nso_product_version)
        except KeyError:
            before = self.nso_product_version
            data = await self.get_version()
            self.__new_version_cache = data
            after = data["nso_version"]

            if before != after:
                logging.warning(
                    f"Failed to get NSO token (NintendoSwitchOnlineService.get_nso_token) with the {before} version. "
                    f"Trying again with the cached version ({after})."
                )

            return await fetch(after)

    async def get_switch_account(self, friend_code: str, nso_token: str) -> SwitchAccount:
        async with ClientSession() as session:
            async with session.post(
                "https://api-lp1.znc.srv.nintendo.net/v3/Friend/GetUserByFriendCode",
                json={"parameter": {"friendCode": friend_code}},
                headers={"Authorization": "Bearer {}".format(nso_token)},
            ) as resp:
                data = await resp.json()

                if "errorMessage" in data or resp.status != 200:
                    raise FailedToGetNintendoSwitchAccount

                result = data["result"]

                return {
                    "extras": result["extras"],
                    "id": result["id"],
                    "name": result["name"],
                    "image_uri": result["imageUri"],
                    "nsa_id": result["nsaId"],
                }

    async def create_friend_request(self, target_nsa_id: str, nso_token: str) -> None:
        async with ClientSession() as session:
            async with session.post(
                "https://api-lp1.znc.srv.nintendo.net/v3/FriendRequest/Create",
                json={"parameter": {"nsaId": target_nsa_id}},
                headers={"Authorization": "Bearer {}".format(nso_token)},
            ) as resp:
                data = await resp.json()

                if "errorMessage" in data or resp.status != 200:
                    raise FailedToSendFriendRequest
                return
