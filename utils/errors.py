from __future__ import annotations

import traceback
from typing import TYPE_CHECKING

from discord import ApplicationCommandError
from discord.ext.commands import CommandError

__all__ = ("BotError", "get_error_message")

if TYPE_CHECKING:
    from .constants import LocaleDict


class BotError(ApplicationCommandError, CommandError):
    """Botのエラーを表すクラス.
    スラッシュコマンドとテキストコマンドの両方で処理できるようにApplicationCommandErrorとCommandErrorを継承している.
    """

    if TYPE_CHECKING:
        message: LocaleDict

    def __init__(self, message: LocaleDict):
        self.message = message


def get_error_message(error: Exception) -> str:
    """エラーのメッセージを取得する.

    Parameters
    ----------
    error : Exception
        エラー.

    Returns
    -------
    str
        エラーのメッセージ.
    """
    return "".join(traceback.format_exception(type(error), error, error.__traceback__))
