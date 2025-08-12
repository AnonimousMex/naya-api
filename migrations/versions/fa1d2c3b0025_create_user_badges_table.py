"""create_user_badges_table

Revision ID: fa1d2c3b0025
Revises: 1da529dc74e9
Create Date: 2025-08-07 20:17:25.355079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa1d2c3b0025'
down_revision: Union[str, None] = '1da529dc74e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_badges",
        sa.Column("id", sa.Uuid(), nullable=False),        
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("badge_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["badge_id"],
            ["badges.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("user_badges")
