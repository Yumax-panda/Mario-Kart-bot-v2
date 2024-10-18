from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from utils.errors import BotError

__all__ = ("is_ignored_channel", "guild_only")


if TYPE_CHECKING:
    from utils.types import HybridContext


def is_ignored_channel(ctx: HybridContext, ignore_ids: Sequence[int], error: bool = True) -> bool:
    """無視するチャンネルかどうかを判定する.

    Parameters
    ----------
    ctx : HybridContext
        コマンドのコンテキスト.
    ignore_ids : Sequence[int]
        無視するチャンネルID.
    error : bool, optional
        無視するチャンネルだった場合, エラーを発生させるかどうか, by default True.

    Returns
    -------
    bool
        無視するチャンネルの場合はTrue.

    Raises
    ------
    BotError
        コマンドが実行不可能な場合.
    """
    ignored = ctx.channel is not None and ctx.channel.id in ignore_ids

    if ignored and error:
        raise BotError(
            {
                "ja": "このコマンドはこのチャンネルでは実行できません。",
                "en-US": "This command cannot be executed in this channel.",
            }
        )

    return ignored


def guild_only(ctx: HybridContext) -> bool:
    """ギルドが存在するかどうかを判定する.

    Parameters
    ----------
    ctx : HybridContext
        コマンドのコンテキスト.

    Returns
    -------
    bool
        ギルドが存在する場合はTrue.

    Raises
    ------
    BotError
        ギルドが存在しない場合.
    """
    if ctx.guild is None:
        raise BotError(
            {
                "ja": "このコマンドはDMでは実行できません。",
                "en-US": "This command cannot be executed in DM.",
            }
        )

    return True
