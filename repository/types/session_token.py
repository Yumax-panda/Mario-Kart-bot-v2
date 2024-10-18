from __future__ import annotations

from abc import ABCMeta, abstractmethod

__all__ = ("SessionTokenRepository",)


class SessionTokenRepository(metaclass=ABCMeta):
    @abstractmethod
    async def put_session_token(self, user_id: int, session_token: str) -> None:
        """フレンド申請をするためのセッショントークンを保存する.

        Parameters
        ----------
        user_id : int
            ユーザーのdiscord ID.
        session_token : str
            セッショントークン.
        """
        ...

    @abstractmethod
    async def get_session_token(self, user_id: int) -> str | None:
        """フレンド申請をするためのセッショントークンを取得する.

        Parameters
        ----------
        user_id : int
            ユーザーID.

        Returns
        -------
        str | None
            セッショントークン.
        """
        ...
