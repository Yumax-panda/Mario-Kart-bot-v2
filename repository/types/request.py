from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

__all__ = ("RequestRepository",)

if TYPE_CHECKING:
    from model.requests import RequestPayload


class RequestRepository(metaclass=ABCMeta):
    @abstractmethod
    async def put_requests(self, user_id: int, data: RequestPayload) -> None:
        """フレンド申請の情報を上書き保存する.

        Parameters
        ----------
        user_id : int
            フレンド申請を保存するユーザーのdiscord ID.
        data : RequestPayload
            フレンド申請のデータ.
        """
        ...

    @abstractmethod
    async def get_requests(self, user_id: int) -> RequestPayload:
        """フレンド申請の情報を取得する.

        Parameters
        ----------
        user_id : int
            フレンド申請を取得するユーザーのdiscord ID.

        Returns
        -------
        RequestPayload
            フレンド申請の情報.
        """
        ...
