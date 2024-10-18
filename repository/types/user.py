from __future__ import annotations

from abc import ABCMeta, abstractmethod

__all__ = ("UserRepository",)


class UserRepository(metaclass=ABCMeta):
    @abstractmethod
    async def put_lounge_id(self, user_id: int, lounge_id: int) -> None:
        """指定したラウンジのIDをユーザーに紐付ける.

        Parameters
        ----------
        user_id : int
            ユーザーのdiscord ID
        lounge_id : int
            ラウンジに登録しているユーザーのdiscord ID
        """
        ...

    @abstractmethod
    async def get_lounge_id(self, user_id: int) -> int | None:
        """指定したユーザーのラウンジのIDを取得する.

        Parameters
        ----------
        user_id : int
            ユーザーのdiscord ID

        Returns
        -------
        int | None
            ラウンジに登録しているユーザーのdiscord ID
        """
        ...
