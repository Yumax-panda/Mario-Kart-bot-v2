from __future__ import annotations

from datetime import timedelta
from io import BytesIO
from typing import TYPE_CHECKING, TypedDict

import pandas as pd
from discord import ApplicationContext, Attachment, Embed, EmbedAuthor, EmbedField, File
from discord.ext.commands import Paginator

from figure.result import create_result_graph
from mk8dx.game import Game
from utils.constants import EmbedColor
from utils.constants.timezone import get_offset
from utils.format import format_result_datetime as fmt_date, format_scores, win_or_lose
from utils.parser import get_datetime, parse_natural_numbers

from .errors import (
    EnemyNameNotFound,
    GuildNotFound,
    InvalidCSVFile,
    InvalidDatetimeInput,
    InvalidGameMessage,
    InvalidScoreInput,
    NoParametersSpecified,
    NotCSVFile,
    QueriedResultNotFound,
    ResultNotFound,
)
from .types import BaseHandler as IBaseHandler, ResultHandler as IResultHandler
from .utils import SimplifiedPaginator

__all__ = ("ResultHandler",)

if TYPE_CHECKING:
    from datetime import datetime

    from discord import Message

    from model.results import ResultItem, ResultItemWithID, Results
    from utils.types import HybridContext

    class UpdateResultParams(TypedDict, total=False):
        played_at: datetime
        score: int
        enemy: str
        enemy_score: int


TOTAL_SCORE = 984


class ResultHandler(IBaseHandler, IResultHandler):
    async def result_list(self, ctx: ApplicationContext, enemy: str | None) -> None:
        await ctx.defer()

        if ctx.guild_id is None:
            raise GuildNotFound

        results = await self.repo.get_results(ctx.guild_id)

        if not results:
            raise ResultNotFound

        df = to_result_df(results)
        paginator = create_result_paginator(df, enemy=enemy)

        await paginator.respond(ctx.interaction)

    async def result_graph(self, ctx: HybridContext) -> None:
        if isinstance(ctx, ApplicationContext):
            await ctx.defer()

        if not (ctx.guild is not None and ctx.guild.id is not None):
            raise GuildNotFound

        results = await self.repo.get_results(ctx.guild.id)

        if not results:
            raise ResultNotFound

        buffer = create_result_graph(
            [
                {
                    "score": result["score"],
                    "enemyScore": result["enemyScore"],
                }
                for result in results
            ]
        )
        file = File(buffer, filename="result.png")

        if isinstance(ctx, ApplicationContext):
            await ctx.respond(file=file)
            return
        await ctx.send(file=file)

    async def message_result_register(self, ctx: ApplicationContext, message: Message) -> None:
        await ctx.defer()

        if not Game.is_valid_message(message):
            raise InvalidGameMessage

        game = Game.from_message(message)
        score, enemy_score = game.get_total_scores()
        created_at = message.created_at + timedelta(hours=get_offset(ctx.locale))

        await self.repo.create_result(
            guild_id=ctx.guild_id,
            played_at=created_at,
            score=score,
            enemy=game.teams[1],
            enemy_score=enemy_score,
        )

        score_preview = format_scores([score, enemy_score])
        tag = f"{game.teams[0]} vs. {game.teams[1]}\n"
        content = "戦績を登録しました.\n" if game.locale == "ja" else "Registered the result.\n"

        await ctx.respond(tag + content + score_preview)

    async def result_register(self, ctx: ApplicationContext, enemy: str, scores: str, datetime_text: str) -> None:
        await ctx.defer()

        if ctx.guild_id is None:
            raise GuildNotFound

        dt = get_datetime(datetime_text, ctx.locale)
        if dt is None:
            raise InvalidDatetimeInput

        nums = parse_natural_numbers(scores)
        if len(nums) != 1 and len(nums) != 2:
            raise InvalidScoreInput

        enemy_score = nums[1] if len(nums) == 2 else TOTAL_SCORE - nums[0]

        await self.repo.create_result(
            guild_id=ctx.guild_id,
            played_at=dt,
            score=nums[0],
            enemy=enemy,
            enemy_score=enemy_score,
        )

        embed = Embed(
            title="登録完了",
            fields=[
                EmbedField(name="敵チーム", value=enemy),
                EmbedField(
                    name="得点",
                    value=format_scores([nums[0], enemy_score]),
                ),
                EmbedField(name="対戦日時", value=fmt_date(dt)),
            ],
            color=EmbedColor.default,
            author=EmbedAuthor(name="created by " + ctx.author.display_name, icon_url=ctx.author.display_avatar.url),
        )

        await ctx.respond(embed=embed)

    async def result_delete(self, ctx: ApplicationContext, id: int | None) -> None:
        await ctx.defer()

        if ctx.guild_id is None:
            raise GuildNotFound

        if id is None:
            results = await self.repo.get_results(ctx.guild_id)

            if not results:
                raise ResultNotFound

            target: ResultItemWithID = results[-1]
            id = target["id"]
        else:
            _target = await self.repo.get_result(ctx.guild_id, id)
            if _target is None:
                raise QueriedResultNotFound

            target = {
                "id": id,
                **_target,
            }

        await self.repo.delete_result(
            guild_id=ctx.guild_id,
            result_id=id,
        )

        embed = Embed(
            title=f"削除完了 (ID: {id})",
            fields=[
                EmbedField(name="敵チーム", value=target["enemy"]),
                EmbedField(name="得点", value=format_scores([target["score"], target["enemyScore"]])),
                EmbedField(name="対戦日時", value=fmt_date(target["date"])),
            ],
            color=EmbedColor.default,
            author=EmbedAuthor(name="deleted by " + ctx.author.display_name, icon_url=ctx.author.display_avatar.url),
        )

        await ctx.respond(embed=embed)

    async def result_edit(
        self,
        ctx: ApplicationContext,
        id: int | None,
        enemy: str | None,
        scores: str | None,
        datetime_text: str | None,
    ) -> None:
        await ctx.defer()

        guild_id: int | None = ctx.guild_id

        if guild_id is None:
            raise GuildNotFound

        if id is None:
            results = await self.repo.get_results(guild_id)

            if not results:
                raise ResultNotFound

            current = results[-1]
            original: ResultItemWithID = current.copy()
            id = current["id"]
        else:
            _original = await self.repo.get_result(guild_id, id)
            if _original is None:
                raise QueriedResultNotFound

            original = {
                "id": id,
                **_original,
            }

        params: UpdateResultParams = {}
        fields: list[EmbedField] = []

        def transition(before: str, after: str) -> str:
            return f"{before} -> {after}"

        if enemy is not None:
            params["enemy"] = enemy
            fields.append(EmbedField(name="敵チーム", value=transition(original["enemy"], enemy)))

        if scores is not None:
            nums = parse_natural_numbers(scores)
            if len(nums) != 1 and len(nums) != 2:
                raise InvalidScoreInput

            params["score"] = nums[0]
            params["enemy_score"] = nums[1] if len(nums) == 2 else TOTAL_SCORE - nums[0]

            before = format_scores([original["score"], original["enemyScore"]], compact=True)
            after = format_scores([params["score"], params["enemy_score"]], compact=True)

            fields.append(EmbedField(name="得点", value=transition(before, after)))

        if datetime_text is not None:
            dt = get_datetime(datetime_text, ctx.locale)
            if dt is None:
                raise InvalidDatetimeInput

            params["played_at"] = dt

            before = fmt_date(original["date"])
            after = fmt_date(dt)

            fields.append(EmbedField(name="対戦日時", value=transition(before, after)))

        if not fields:
            raise NoParametersSpecified

        await self.repo.update_result(
            guild_id=guild_id,
            result_id=id,
            **params,
        )

        embed = Embed(
            title=f"編集完了 (ID: {id})",
            fields=fields,
            color=EmbedColor.default,
            author=EmbedAuthor(name="edited by " + ctx.author.display_name, icon_url=ctx.author.display_avatar.url),
        )

        await ctx.respond(embed=embed)

    async def result_data_export(self, ctx: ApplicationContext) -> None:
        await ctx.defer()

        if ctx.guild is None or ctx.guild.id is None:
            raise GuildNotFound

        results = await self.repo.get_results(ctx.guild.id)

        if not results:
            raise ResultNotFound

        team_name = await self.repo.get_team_name(ctx.guild.id) or ctx.guild.name

        # TODO: CSVセーフなチーム名に変換する

        df = pd.DataFrame(results)
        df.insert(0, "team", team_name)

        buffer = BytesIO()
        df.to_csv(buffer, index=False, header=False, columns=["team", "score", "enemyScore", "enemy", "date"])
        buffer.seek(0)

        file = File(buffer, filename="results.csv")

        await ctx.respond(file=file)

    async def result_data_import(self, ctx: ApplicationContext, file: Attachment) -> None:
        await ctx.defer()

        extension = file.filename.split(".")[-1]
        if extension != "csv":
            raise NotCSVFile

        if ctx.guild_id is None:
            raise GuildNotFound

        buffer = BytesIO()
        await file.save(buffer)

        try:
            df = pd.read_csv(
                buffer,
                skipinitialspace=True,
                header=None,
                dtype={0: str, 1: int, 2: int, 3: str},
                keep_default_na=False,  # 例えば、チーム名が"null"のような場合にNaNとしてパースしないようにする
            ).loc[:, [1, 2, 3, 4]]
            df.columns = ["score", "enemyScore", "enemy", "date"]
            df = df.copy()
            df["date"] = pd.to_datetime(df["date"])
        except Exception:
            raise InvalidCSVFile from None

        results = to_list(df)
        await self.repo.put_results(ctx.guild_id, results)

        await ctx.respond("戦績ファイルを読みこみました.")


def to_result_df(results: list[ResultItemWithID]) -> pd.DataFrame:
    """戦績をデータフレームに変換する. 日付の昇順でソートされる. 重複したデータは削除される.

    Parameters
    ----------
    results : Results
        戦績のデータ. 少なくとも1つの戦績が含まれている必要がある.

    Returns
    -------
    pd.DataFrame
        戦績のデータフレーム. 日付の昇順でソートされている. dateキーの値はdatetime型に変換されている.
    """
    df = pd.DataFrame(results)
    df = df.copy()
    df["score"] = df["score"]
    df["enemyScore"] = df["enemyScore"]
    return df


def to_list(result_df: pd.DataFrame) -> Results:
    """戦績のデータフレームを日付の昇順にソートしたあと, リストに変換する. 重複したデータは削除される.

    Parameters
    ----------
    result_df : pd.DataFrame
        データフレーム

    Returns
    -------
    list[dict[str, Any]]
        リスト
    """
    return result_df.to_dict(orient="records")


def create_result_paginator(results: pd.DataFrame, enemy: str | None = None) -> SimplifiedPaginator:
    """戦績を表示するためのページを作成する.

    Parameters
    ----------
    results : pd.DataFrame
        戦績のデータフレーム
    enemy : str, optional
        絞り込む相手の名前, by default None

    Returns
    -------
    SimplifiedPaginator
        戦績を表示するためのページ

    Raises
    ------
    EnemyNameNotFound
        指定された相手の名前が見つからない場合
    """
    if enemy is not None:
        df = results.query(f"enemy == '{enemy}'").copy()

        if df.empty:
            name_prefix = enemy[0].lower()
            enemy_names: list[str] = results["enemy"].unique().tolist()
            similar = [n for n in enemy_names if n[0].lower() == name_prefix]
            raise EnemyNameNotFound(similar)

    else:
        df = results.copy()

    df["fmt_score"] = df["score"].astype(str) + " - " + df["enemyScore"].astype(str)
    df["diff"] = df["score"] - df["enemyScore"]
    df["fmt_date"] = df["date"].dt.strftime("%Y/%m/%d")

    if enemy is not None:
        columns = ["id", "fmt_date", "fmt_score", "diff"]
    else:
        columns = ["id", "fmt_score", "enemy", "diff"]

    lines = df.to_string(
        columns=columns,
        formatters={"diff": win_or_lose},
        header=False,
        justify="center",
        index=False,
    ).split("\n")

    win, lose, draw = (
        df[df["diff"] > 0].shape[0],
        df[df["diff"] < 0].shape[0],
        df[df["diff"] == 0].shape[0],
    )

    footer = f"__**Win**__:  {win}  __**Lose**__:  {lose}  __**Draw**__:  {draw}  [{len(df)}]"

    title = f"vs.  **{enemy}**" if enemy is not None else ""
    prefix = f"{title}```"
    suffix = f"```{footer}"

    paginator = Paginator(prefix=prefix, suffix=suffix, max_size=900)

    for line in lines:
        paginator.add_line(line)

    return SimplifiedPaginator(pages=paginator.pages)
