"""create_sounds_game_sounds_table

Revision ID: 8a9e650afe5b
Revises: 770d920ee889
Create Date: 2025-07-26 21:18:07.802824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '8a9e650afe5b'
down_revision: Union[str, None] = '770d920ee889'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
      op.create_table(
        "sounds_game_sounds",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column('audio_path', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("emotion_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["emotion_id"], ["emotions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
     op.drop_table('sounds_game_sounds')
