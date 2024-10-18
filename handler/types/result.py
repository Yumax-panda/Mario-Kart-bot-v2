from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

__all__ = ("ResultHandler",)

if TYPE_CHECKING:
    from discord import ApplicationContext, Attachment, Message

    from utils.types import HybridContext


class ResultHandler(metaclass=ABCMeta):
    @abstractmethod
    async def result_list(self, ctx: ApplicationContext, enemy: str | None) -> None:
        """戦績を表示する.

        Parameters
        ----------
        ctx : ApplicationContext
            コマンドのコンテキスト.
        enemy : str | None
            表示する戦績を絞り込む相手チーム名. 指定しない場合は全ての戦績を表示する.
        """
        ...

    @abstractmethod
    async def result_graph(self, ctx: HybridContext) -> None:
        """戦績をグラフで表示する.

        Parameters
        ----------
        ctx : HybridContext
            コマンドのコンテキスト.
        """
        ...

    @abstractmethod
    async def message_result_register(self, ctx: ApplicationContext, message: Message) -> None:
        """即時集計の埋め込みメッセージから戦績を登録する.

        Parameters
        ----------
        ctx : ApplicationContext
            コマンドのコンテキスト.
        message : Message
            戦績を登録する埋め込みメッセージ.
        """
        ...

    @abstractmethod
    async def result_register(self, ctx: ApplicationContext, enemy: str, scores: str, datetime_text: str) -> None:
        """戦績を登録する.

        Parameters
        ----------
        ctx : ApplicationContext
            コマンドのコンテキスト.
        enemy : str
            対戦相手のチーム名.
        scores : str
            自分のチームの得点. 相手のチームの得点を省略可能.
        datetime_text : str
            戦績の日時を表す文字列. 2024-06-05-21, 06-05-21, 21のような形式.
        """
        ...

    @abstractmethod
    async def result_delete(self, ctx: ApplicationContext, id: int | None) -> None:
        """戦績を削除する.

        Parameters
        ----------
        ctx : ApplicationContext
            コマンドのコンテキスト.
        id : int | None
            削除する戦績のID. 指定しない場合は最新の戦績を削除する.
        """
        ...

    @abstractmethod
    async def result_edit(
        self,
        ctx: ApplicationContext,
        id: int | None,
        enemy: str | None,
        scores: str | None,
        datetime_text: str | None,
    ) -> None:
        """戦績を編集する.

        Parameters
        ----------
        ctx : ApplicationContext
            コマンドのコンテキスト.
        id : int | None
            編集する戦績のID. 指定しない場合は最新の戦績を編集する.
        enemy : str | None
            対戦相手のチーム名.
        scores : str | None
            自分のチームの得点. 相手のチームの得点を省略可能.
        datetime_text : str | None
            戦績の日付. 2024-06-05-21, 06-05-21, 21のような形式.
        """
        ...

    @abstractmethod
    async def result_data_export(self, ctx: ApplicationContext) -> None:
        """戦績データをCSVファイルとしてエクスポートする.

        Parameters
        ----------
        ctx : ApplicationContext
            コマンドのコンテキスト.
        """
        ...

    @abstractmethod
    async def result_data_import(self, ctx: ApplicationContext, file: Attachment) -> None:
        """戦績データをCSVファイルからインポートする.

        Parameters
        ----------
        ctx : ApplicationContext
            コマンドのコンテキスト.
        file : Attachment
            インポートするファイル.
        """
        ...
