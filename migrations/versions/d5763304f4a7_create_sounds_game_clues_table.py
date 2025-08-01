"""create_sounds_game_clues_table

Revision ID: d5763304f4a7
Revises: 8a9e650afe5b
Create Date: 2025-07-28 19:02:44.329817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'd5763304f4a7'
down_revision: Union[str, None] = '8a9e650afe5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sounds_game_clues",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("sound_id", sa.Uuid(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('body', sqlmodel.sql.sqltypes.AutoString(length=150), nullable=False),
        sa.Column('tip', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('highlight', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.ForeignKeyConstraint(["sound_id"], ["sounds_game_sounds.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table('sounds_game_clues')
