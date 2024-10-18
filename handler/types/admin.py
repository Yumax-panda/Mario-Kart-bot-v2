from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

__all__ = ("AdminHandler",)

if TYPE_CHECKING:
    from utils.types import HybridContext


class AdminHandler(metaclass=ABCMeta):
    @abstractmethod
    async def resolve_command_error(self, ctx: HybridContext, error: Exception) -> None:
        """エラーが発生した際に呼び出されるメソッド. 想定されるエラーの場合、メッセージをコマンドの実行者に送信する.
        想定されていないエラーの場合、エラーの詳細をファイルに書き込み、Webhookを通じてログチャンネルへ送信する.

        Parameters
        ----------
        ctx : HybridContext
            エラーが起きたコマンドのコンテキスト.
        error : Exception
            発生したエラー.
        """
        ...
