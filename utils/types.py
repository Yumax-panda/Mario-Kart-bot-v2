from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from discord import ApplicationContext, Member, Message, User, WebhookMessage
from discord.ext import commands

__all__ = (
    "Context",
    "HybridContext",
    "HybridMember",
    "HybridMessage",
)

if TYPE_CHECKING:
    from bot import Bot

# WARNING: TYPE_CHECKINGを使っているため, cogsのコマンドコールバックのアノテーションとして使わないこと
Context: TypeAlias = commands.Context[Bot]
HybridContext: TypeAlias = Context | ApplicationContext
HybridMember: TypeAlias = Member | User
HybridMessage: TypeAlias = Message | WebhookMessage
