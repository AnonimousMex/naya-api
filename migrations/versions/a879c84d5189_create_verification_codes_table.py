"""Create verification_codes table

Revision ID: 354b21b44667
Revises: 94eb8ee94ebf
Create Date: 2025-05-25 22:42:03.401693
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel


# Revision identifiers, used by Alembic.
revision: str = "a879c84d5189"
down_revision: Union[str, None] = "1d4418412945"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "verification_codes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("code", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("is_alive", sa.Boolean(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )


def downgrade() -> None:
    op.drop_table("verification_codes")
