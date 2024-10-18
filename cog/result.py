from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Attachment, SlashCommandGroup, message_command, option
from discord.ext import commands
from discord.ext.commands import BucketType, MaxConcurrency

from .core import Cog

if TYPE_CHECKING:
    from discord import ApplicationContext, Message

    from bot import Bot


class ResultCog(Cog, name="Result"):
    def __init__(self, bot: Bot) -> None:
        super().__init__(
            bot,
            description="Manage results.",
            description_localizations={
                "ja": "戦績管理",
                "en-US": "Manage results.",
            },
        )

    result = SlashCommandGroup(
        name="result",
        guild_only=True,
        max_concurrency=MaxConcurrency(1, per=BucketType.guild, wait=False),
    )

    @result.command(
        name="list",
        description="Show all results.",
        description_localizations={
            "ja": "全ての戦績を表示",
        },
    )
    @option(
        name="enemy",
        type=str,
        description="Filter by enemy team name.",
        description_localizations={
            "ja": "指定した場合, 相手チーム名で絞り込む",
        },
        required=False,
        default=None,
    )
    async def result_list(self, ctx: ApplicationContext, enemy: str | None) -> None:
        return await self.h.result_list(ctx, enemy=enemy)

    @result.command(
        name="graph",
        description="Show result graph",
        description_localizations={
            "ja": "戦績のグラフを表示",
        },
    )
    async def result_graph(self, ctx: ApplicationContext) -> None:
        return await self.h.result_graph(ctx)

    @commands.command(
        name="graph",
        description="Show result graph",
        brief="戦績グラフを表示",
        usage="!graph",
        hidden=False,
    )
    async def text_result_graph(self, ctx: commands.Context) -> None:
        return await self.h.result_graph(ctx)

    @result.command(
        name="register",
        description="Register a result.",
        description_localizations={
            "ja": "戦績を登録",
        },
    )
    @option(
        name="enemy",
        type=str,
        description="Enemy team name.",
        description_localizations={
            "ja": "対戦相手のチーム名",
        },
        required=True,
    )
    @option(
        name="scores",
        type=str,
        description="Scores of your team and enemy team. (e.g. 500 484)",
        description_localizations={
            "ja": "<自チームの得点> <相手チームの得点: 省略可> の形式 (例: 500 484)",
        },
        required=True,
    )
    @option(
        name="datetime",
        parameter_name="datetime_text",
        type=str,
        description="Date of the result. (e.g. 2024 6 5 21, 06 05 21, 21)",
        description_localizations={
            "ja": "戦績の日付 (例: 2024 6 5 21, 06 05 21, 21)",
        },
        required=True,
    )
    async def result_register(
        self,
        ctx: ApplicationContext,
        enemy: str,
        scores: str,
        datetime_text: str,
    ) -> None:
        return await self.h.result_register(ctx, enemy, scores, datetime_text)

    @message_command(name="Register Result")
    @commands.guild_only()
    async def message_result_register(self, ctx: ApplicationContext, message: Message) -> None:
        return await self.h.message_result_register(ctx, message)

    @result.command(
        name="delete",
        description="Delete a result.",
        description_localizations={
            "ja": "戦績を削除",
        },
    )
    @option(
        name="id",
        type=int,
        description="ID of the result to delete. If not specified, the latest result will be deleted.",
        description_localizations={
            "ja": "削除する戦績のID. 指定しない場合は最新の戦績を削除する.",
        },
        required=False,
        default=None,
    )
    async def result_delete(self, ctx: ApplicationContext, id: int | None) -> None:
        return await self.h.result_delete(ctx, id)

    @result.command(
        name="edit",
        description="Edit a result.",
        description_localizations={
            "ja": "戦績を編集",
        },
    )
    @option(
        name="id",
        type=int,
        description="ID of the result to edit. If not specified, the latest result will be edited.",
        description_localizations={
            "ja": "編集する戦績のID. 指定しない場合は最新の戦績を編集する.",
        },
        required=False,
        default=None,
    )
    @option(
        name="enemy",
        type=str,
        description="Enemy team name.",
        description_localizations={
            "ja": "対戦相手のチーム名",
        },
        required=False,
        default=None,
    )
    @option(
        name="scores",
        type=str,
        description="Scores of your team and enemy team. (e.g. 500 484)",
        description_localizations={
            "ja": "<自チームの得点> <相手チームの得点: 省略可> の形式 (例: 500 484)",
        },
        required=False,
        default=None,
    )
    @option(
        name="datetime",
        parameter_name="datetime_text",
        type=str,
        description="Date of the result. (e.g. 2024 6 5 21, 06 05 21, 21)",
        description_localizations={
            "ja": "戦績の日付 (例: 2024 6 5 21, 06 05 21, 21)",
        },
        required=False,
        default=None,
    )
    async def result_edit(
        self,
        ctx: ApplicationContext,
        id: int | None,
        enemy: str | None,
        scores: str | None,
        datetime_text: str | None,
    ) -> None:
        return await self.h.result_edit(ctx, id, enemy, scores, datetime_text)

    data = result.create_subgroup(name="data")

    @data.command(
        name="export",
        description="Export result data.",
        description_localizations={
            "ja": "戦績データをCSVファイルとして出力",
        },
    )
    async def result_data_export(self, ctx: ApplicationContext) -> None:
        return await self.h.result_data_export(ctx)

    @data.command(
        name="import",
        description="Import result data.",
        description_localizations={
            "ja": "戦績データをCSVファイルから読み込む.",
        },
    )
    @option(
        name="csv",
        parameter_name="file",
        type=Attachment,
        description="File to import result data (CSV only).",
        description_localizations={
            "ja": "読み込む戦績のファイル (CSV形式).",
        },
        required=True,
    )
    async def result_data_import(self, ctx: ApplicationContext, file: Attachment) -> None:
        return await self.h.result_data_import(ctx, file)


def setup(bot: Bot) -> None:
    bot.add_cog(ResultCog(bot))
