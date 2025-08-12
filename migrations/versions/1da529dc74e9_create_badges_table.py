"""create_badges_table

Revision ID: 1da529dc74e9
Revises: 056dc2723767
Create Date: 2025-08-07 19:10:01.825273

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '1da529dc74e9'
down_revision: Union[str, None] = '056dc2723767'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "badges",
        sa.Column("id", sa.Uuid(), nullable=False),        
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('image_path', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),

        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table('badges')