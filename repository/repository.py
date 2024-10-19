from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Iterable, TypeVar

from sqlalchemy import and_, delete, desc, select
from sqlalchemy.dialects.mysql import insert

from model.gathers import gathers
from model.guilds import guilds
from model.nso_tokens import nso_tokens
from model.pinned_players import PinnedPlayer, pinned_players
from model.requests import requests
from model.results import results as results_table
from model.session_tokens import session_tokens
from model.users import users

from .types.repository import Repository as IRepository

__all__ = ("Repository",)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

    from model.gathers import GatherItem, ParticipationType
    from model.requests import RequestPayload
    from model.results import ResultItemWithID, Results


RepoT = TypeVar("RepoT", bound="Repository")


class Repository(IRepository):

    if TYPE_CHECKING:
        engine: AsyncEngine

    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    # GatherRepository implementation
    async def insert_gathers(
        self,
        guild_id: int,
        user_ids: Iterable[int],
        type: ParticipationType,
        hours: Iterable[int],
    ) -> None:
        async with self.engine.begin() as conn:
            values = [
                {
                    "guild_id": guild_id,
                    "user_id": user_id,
                    "type": type,
                    "hour": hour,
                }
                for user_id in user_ids
                for hour in hours
            ]

            await conn.execute(gathers.insert(), values)

    async def delete_gathers(
        self,
        guild_id: int,
        user_ids: Iterable[int],
        hours: Iterable[int],
    ) -> None:
        async with self.engine.begin() as conn:
            query = gathers.delete().where(
                and_(
                    gathers.c.guild_id == guild_id,
                    gathers.c.user_id.in_(user_ids),
                    gathers.c.hour.in_(hours),
                ),
            )

            await conn.execute(query)

    async def delete_all_gathers_by_hours(self, guild_id: int, hours: Iterable[int]) -> None:
        async with self.engine.begin() as conn:
            query = gathers.delete().where(
                and_(
                    gathers.c.guild_id == guild_id,
                    gathers.c.hour.in_(hours),
                ),
            )

            await conn.execute(query)

    async def clear_gathers(self, guild_id: int) -> None:
        async with self.engine.begin() as conn:
            query = gathers.delete().where(gathers.c.guild_id == guild_id)
            await conn.execute(query)

    async def get_all_gathers(self, guild_id: int) -> list[GatherItem]:
        async with self.engine.begin() as conn:
            query = select(
                gathers.c.guild_id,
                gathers.c.user_id,
                gathers.c.type,
                gathers.c.hour,
            ).where(gathers.c.guild_id == guild_id)

            result = await conn.execute(query)
            records = result.fetchall()

            return [
                {
                    "guild_id": g_id,
                    "user_id": u_id,
                    "type": t,
                    "hour": h,
                }
                for (g_id, u_id, t, h) in records
            ]

    # GuildRepository implementation
    async def put_team_name(self, guild_id: int, team_name: str) -> None:
        async with self.engine.connect() as conn:
            async with conn.begin() as tx:
                try:
                    query = insert(guilds).values(id=guild_id, name=team_name).on_duplicate_key_update(name=team_name)
                    await conn.execute(query)
                    await tx.commit()
                except:
                    await tx.rollback()

    async def get_team_name(self, guild_id: int) -> str | None:
        async with self.engine.begin() as conn:
            query = select(guilds.c.name).where(guilds.c.id == guild_id)
            result = await conn.execute(query)
            data = result.fetchone()

        if data is None:
            return None

        (team_name,) = data
        return team_name

    # NSOTokenRepository implementation
    async def put_nso_token(self, user_id: int, nso_token: str, expires_in: int) -> None:
        async with self.engine.begin() as conn:
            now = datetime.now()
            expires_at = now + timedelta(seconds=expires_in)

            query = (
                insert(nso_tokens)
                .values(
                    user_id=user_id,
                    token=nso_token,
                    expires_at=expires_at,
                )
                .on_duplicate_key_update(
                    token=nso_token,
                    expires_at=expires_at,
                )
            )

            await conn.execute(query)

    async def get_nso_token(self, user_id: int) -> str | None:
        async with self.engine.begin() as conn:
            now = datetime.now()
            query = select(nso_tokens.c.token).where(
                and_(
                    nso_tokens.c.user_id == user_id,
                    nso_tokens.c.expires_at > now,
                ),
            )

            result = await conn.execute(query)
            data = result.fetchone()

        if data is None:
            return None

        (nso_token,) = data
        return nso_token

    # PinnedPlayerRepository implementation
    async def put_pinned_player(self, user_id: int, player_id: int, nick_name: str) -> None:
        async with self.engine.connect() as conn:
            async with conn.begin() as tx:
                try:
                    query = (
                        insert(pinned_players)
                        .values(
                            user_id=user_id,
                            bookmarked_player_id=player_id,
                            bookmarked_player_display_name=nick_name,
                        )
                        .on_duplicate_key_update(
                            bookmarked_player_display_name=nick_name,
                        )
                    )
                    await conn.execute(query)
                    await tx.commit()
                except:
                    await tx.rollback()

    async def delete_pinned_player(self, user_id: int, player_id: int) -> None:
        async with self.engine.begin() as conn:
            query = delete(pinned_players).where(
                and_(
                    pinned_players.c.user_id == user_id,
                    pinned_players.c.bookmarked_player_id == player_id,
                ),
            )
            await conn.execute(query)

    async def get_pinned_players(self, user_id: int) -> list[PinnedPlayer]:
        async with self.engine.begin() as conn:
            query = select(
                pinned_players.c.bookmarked_player_id,
                pinned_players.c.bookmarked_player_display_name,
            ).where(pinned_players.c.user_id == user_id)

            result = await conn.execute(query)
            records = result.fetchall()

            return [
                PinnedPlayer(
                    mkc_id=player_id,
                    nick_name=player_display_name,
                )
                for (player_id, player_display_name) in records
            ]

    # RequestRepository implementation
    async def put_requests(self, user_id: int, data: RequestPayload) -> None:
        try:
            await self._delete_all_requests(user_id=user_id)
        except:
            pass

        async with self.engine.begin() as conn:
            values = [
                {
                    "user_id": user_id,
                    "target_user_name": d["name"],
                    "target_user_switch_fc": d["fc"],
                    "target_user_nsa_id": d["nsa_id"],
                }
                for d in data
            ]
            await conn.execute(requests.insert(), values)

    async def _delete_all_requests(self, user_id: int) -> None:
        async with self.engine.begin() as conn:
            query = delete(requests).where(requests.c.user_id == user_id)
            await conn.execute(query)

    async def get_requests(self, user_id: int) -> RequestPayload:
        async with self.engine.begin() as conn:
            query = select(
                requests.c.target_user_switch_fc,
                requests.c.target_user_name,
                requests.c.target_user_nsa_id,
            ).where(requests.c.user_id == user_id)

            result = await conn.execute(query)
            records = result.fetchall()

        return [
            {
                "fc": fc,
                "name": name,
                "nsa_id": nsa_id,
            }
            for (fc, name, nsa_id) in records
        ]

    # ResultRepository implementation
    async def create_result(
        self,
        guild_id: int,
        played_at: datetime,
        score: int,
        enemy: str,
        enemy_score: int,
    ) -> None:
        async with self.engine.begin() as conn:
            query = results_table.insert().values(
                {
                    "guild_id": guild_id,
                    "played_at": played_at,
                    "score": score,
                    "enemy": enemy,
                    "enemy_score": enemy_score,
                }
            )
            await conn.execute(query)

    async def get_result(self, guild_id: int, result_id: int) -> ResultItemWithID | None:
        async with self.engine.begin() as conn:
            query = select(
                results_table.c.id,
                results_table.c.played_at,
                results_table.c.score,
                results_table.c.enemy,
                results_table.c.enemy_score,
            ).where(
                and_(
                    results_table.c.guild_id == guild_id,
                    results_table.c.id == result_id,
                ),
            )

            result = await conn.execute(query)
            data = result.fetchone()

        if data is None:
            return None

        (id, played_at, score, enemy_name, enemy_score) = data
        return {
            "id": id,
            "date": played_at,
            "score": score,
            "enemy": enemy_name,
            "enemyScore": enemy_score,
        }

    async def delete_result(self, guild_id: int, result_id: int) -> None:
        async with self.engine.begin() as conn:
            query = delete(results_table).where(
                and_(
                    results_table.c.guild_id == guild_id,
                    results_table.c.id == result_id,
                ),
            )
            await conn.execute(query)

    async def update_result(
        self,
        guild_id: int,
        result_id: int,
        played_at: datetime | None = None,
        score: int | None = None,
        enemy: str | None = None,
        enemy_score: int | None = None,
    ) -> None:
        async with self.engine.begin() as conn:
            query = results_table.update().where(
                and_(
                    results_table.c.guild_id == guild_id,
                    results_table.c.id == result_id,
                ),
            )

            if played_at is not None:
                query = query.values(played_at=played_at)
            if score is not None:
                query = query.values(score=score)
            if enemy is not None:
                query = query.values(enemy=enemy)
            if enemy_score is not None:
                query = query.values(enemy_score=enemy_score)

            await conn.execute(query)

    async def _delete_all_results(self, guild_id: int) -> None:
        async with self.engine.begin() as conn:
            query = delete(results_table).where(results_table.c.guild_id == guild_id)
            await conn.execute(query)

    async def put_results(self, guild_id: int, results: Results) -> None:
        await self._delete_all_results(guild_id=guild_id)

        async with self.engine.begin() as conn:

            values = [
                {
                    "guild_id": guild_id,
                    "played_at": record["date"],
                    "score": record["score"],
                    "enemy": record["enemy"],
                    "enemy_score": record["enemyScore"],
                }
                for record in results
            ]

            await conn.execute(results_table.insert(), values)

    async def get_results(self, guild_id: int) -> list[ResultItemWithID]:
        async with self.engine.begin() as conn:
            query = (
                select(
                    results_table.c.id,
                    results_table.c.played_at,
                    results_table.c.score,
                    results_table.c.enemy,
                    results_table.c.enemy_score,
                )
                .where(results_table.c.guild_id == guild_id)
                .order_by(desc(results_table.c.played_at))
            )

            result = await conn.execute(query)

        data = result.fetchall()

        return [
            {
                "id": id,
                "date": played_at,
                "score": score,
                "enemy": enemy_name,
                "enemyScore": enemy_score,
            }
            for (id, played_at, score, enemy_name, enemy_score) in data
        ]

    # SessionTokenRepository implementation
    async def put_session_token(self, user_id: int, session_token: str) -> None:
        async with self.engine.connect() as conn:
            async with conn.begin() as tx:
                try:
                    query = (
                        insert(session_tokens)
                        .values(user_id=user_id, token=session_token)
                        .on_duplicate_key_update(token=session_token)
                    )
                    await conn.execute(query)
                    await tx.commit()
                except:
                    await tx.rollback()

    async def get_session_token(self, user_id: int) -> str | None:
        async with self.engine.begin() as conn:
            query = select(session_tokens.c.token).where(session_tokens.c.user_id == user_id)
            result = await conn.execute(query)
            data = result.fetchone()

        if data is None:
            return None

        (session_token,) = data
        return session_token

    # UserRepository implementation
    async def put_lounge_id(self, user_id: int, lounge_id: int) -> None:
        async with self.engine.connect() as conn:
            async with conn.begin() as tx:
                try:
                    query = (
                        insert(users)
                        .values(id=user_id, lounge_id=lounge_id)
                        .on_duplicate_key_update(
                            lounge_id=lounge_id,
                        )
                    )
                    await conn.execute(query)
                    await tx.commit()

                except:
                    await tx.rollback()

    async def get_lounge_id(self, user_id: int) -> int | None:
        async with self.engine.begin() as conn:
            query = select(users.c.lounge_id).where(users.c.id == user_id)
            result = await conn.execute(query)
            data = result.fetchone()

        if data is None:
            return None

        (lounge_id,) = data
        return lounge_id
