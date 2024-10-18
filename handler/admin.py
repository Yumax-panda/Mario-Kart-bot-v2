from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

from discord import (
    ApplicationCommand,
    ApplicationCommandInvokeError,
    ApplicationContext,
    CheckFailure as AppCommandCheckFailure,
    Embed,
    File,
    Forbidden,
)
from discord.ext.commands import (
    BotMissingPermissions,
    CheckFailure,
    CommandNotFound,
    MaxConcurrencyReached,
    NoPrivateMessage,
    NotOwner,
    UserInputError,
)

from utils.constants import EmbedColor
from utils.errors import BotError, get_error_message

from .types import AdminHandler as IAdminHandler, BaseHandler as IBaseHandler

__all__ = ("AdminHandler",)

if TYPE_CHECKING:
    from utils.constants import Locale, LocaleDict
    from utils.types import HybridContext


class AdminHandler(IBaseHandler, IAdminHandler):
    async def resolve_command_error(self, ctx: HybridContext, error: Exception) -> None:
        content: LocaleDict | None = None
        locale: Locale = getattr(ctx, "locale", "ja")

        if isinstance(error, BotError):
            content = error.message
        elif isinstance(error, NoPrivateMessage):
            content = {
                "ja": "このコマンドはDM内で実行できません.",
                "en-US": "This command is not available in DM channels.",
            }
        elif isinstance(error, NotOwner):
            content = {
                "ja": "このコマンドは管理者専用です.",
                "en-US": "This command is for administrators only.",
            }
        elif isinstance(error, BotMissingPermissions):
            missing = ", ".join(error.missing_permissions)
            content = {
                "ja": f"このコマンドを使うにはBotへ以下の権限のください: {missing}",
                "en-US": f"The bot needs the following permissions: {missing}",
            }
        elif isinstance(error, UserInputError):
            content = {
                "ja": "入力が無効です. コマンドのヘルプを参照してください.",
                "en-US": "Invalid input. Please refer to the command help.",
            }
        elif isinstance(error, ApplicationCommandInvokeError):
            if isinstance(error.original, Forbidden):
                content = {
                    "ja": "Botへ権限がありません。Botの再導入を試してみてください。",
                    "en-US": "The bot is missing the required permissions. Please try re-inviting the bot.",
                }
        elif isinstance(error, MaxConcurrencyReached):

            display_per: dict[Locale, dict[str, str]] = {
                "ja": {
                    "default": "全体",
                    "user": "ユーザーごと",
                    "guild": "サーバーごと",
                    "channel": "チャンネルごと",
                    "member": "メンバーごと",
                    "category": "カテゴリーごと",
                    "role": "ロールごと",
                },
                "en-US": {
                    "default": "global",
                    "user": "per user",
                    "guild": "per guild",
                    "channel": "per channel",
                    "member": "per member",
                    "category": "per category",
                    "role": "per role",
                },
            }

            per = error.per.name
            max_concurrency = error.number
            content = {
                "ja": f"このコマンドは{display_per[locale][per]}において{max_concurrency}回までしか実行できません. しばらくしてから再度お試しください.",
                "en-US": f"This command can only be executed {max_concurrency} times {display_per[locale][per]}. Please try again later.",
            }

        elif isinstance(error, (CommandNotFound, CheckFailure, AppCommandCheckFailure)):
            return

        if content is not None:
            msg = content.get(locale, content["ja"])
            if isinstance(ctx, ApplicationContext):
                await ctx.respond(msg, ephemeral=True)
            else:
                await ctx.send(msg)

            return

        await self._dispatch_command_error(ctx, error)

        content = {
            "ja": "予期しないエラーが発生しました. 時間をおいて再度お試しください.",
            "en-US": "An unexpected error has occurred. Please try again later.",
        }

        msg = content.get(locale, content["ja"])
        if isinstance(ctx, ApplicationContext):
            await ctx.respond(msg, ephemeral=True)
        else:
            await ctx.send(msg)

    async def _dispatch_command_error(self, ctx: HybridContext, error: Exception) -> None:
        """コマンドのエラーをWebhookを通じてログチャンネルへ送信する.

        Parameters
        ----------
        ctx : HybridContext
            エラーが発生したコマンドのコンテキスト.
        error : Exception
            発生したエラー.
        """
        error_message = get_error_message(error)
        fp = BytesIO(error_message.encode("utf-8"))
        file = File(fp, filename="error.txt")

        embed = Embed(
            title=error.__class__.__name__,
            color=EmbedColor.error,
        )

        command = ctx.command

        if command is None:
            command_name = "Unknown"
        elif isinstance(command, ApplicationCommand):
            command_name = command.qualified_name
        else:
            command_name = command.name

        embed.add_field(name="Command", value=command_name, inline=False)

        if isinstance(ctx, ApplicationContext):
            embed.add_field(name="Inputs", value=f"```{ctx.selected_options}```", inline=False)

        embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)

        await self.webhook.send(embed=embed, file=file)
