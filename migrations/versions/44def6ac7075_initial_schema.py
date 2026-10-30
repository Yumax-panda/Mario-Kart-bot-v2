"""initial schema

Revision ID: 44def6ac7075
Revises: 
Create Date: 2026-10-31 00:17:01.798926

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "44def6ac7075"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "gathers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("guild_id", sa.BigInteger(), nullable=True),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("type", sa.String(length=3), nullable=True),
        sa.Column("hour", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("guild_id", "user_id", "hour"),
    )
    op.create_table(
        "guilds",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "pinned_players",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BIGINT(), nullable=True),
        sa.Column("bookmarked_player_id", sa.BIGINT(), nullable=True),
        sa.Column("bookmarked_player_display_name", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "bookmarked_player_id"),
    )
    op.create_table(
        "results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("guild_id", sa.BigInteger(), nullable=True),
        sa.Column("played_at", sa.DateTime(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("enemy", sa.Text(), nullable=True),
        sa.Column("enemy_score", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("lounge_id", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
    op.drop_table("results")
    op.drop_table("pinned_players")
    op.drop_table("guilds")
    op.drop_table("gathers")
