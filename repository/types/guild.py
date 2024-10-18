from __future__ import annotations

from abc import ABCMeta, abstractmethod

__all__ = ("GuildRepository",)


class GuildRepository(metaclass=ABCMeta):
    @abstractmethod
    async def put_team_name(self, guild_id: int, team_name: str) -> None:
        """指定したギルドのチーム名を更新する.

        Parameters
        ----------
        guild_id : int
            ギルドのID
        team_name : str
            チーム名
        """
        ...

    @abstractmethod
    async def get_team_name(self, guild_id: int) -> str | None:
        """指定したギルドのチーム名を取得する.

        Parameters
        ----------
        guild_id : int
            ギルドのID

        Returns
        -------
        str | None
            チーム名
        """
        ...
