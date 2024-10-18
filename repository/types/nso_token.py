from __future__ import annotations

from abc import ABCMeta, abstractmethod

__all__ = ("NSOTokenRepository",)


class NSOTokenRepository(metaclass=ABCMeta):
    @abstractmethod
    async def put_nso_token(self, user_id: int, nso_token: str, expires_in: int) -> None:
        """Nintendo Switch Onlineのトークンを保存する.

        Parameters
        ----------
        user_id : int
            ユーザーID.
        nso_token : str
            トークン.
        expires_in : int
            有効期限.
        """
        ...

    @abstractmethod
    async def get_nso_token(self, user_id: int) -> str | None:
        """Nintendo Switch Onlineのトークンを取得する.

        Parameters
        ----------
        user_id : int
            ユーザーID.

        Returns
        -------
        str | None
            トークン.
        """
        ...
