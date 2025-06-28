"""create_verification_codes_password_reset_table

Revision ID: 40325f49d943
Revises: 20b278db0ff8
Create Date: 2025-06-26 05:49:50.267139

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '40325f49d943'
down_revision: Union[str, None] = '20b278db0ff8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "verification_codes_password_reset",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("is_alive", sa.Boolean(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("verification_codes_password_reset")
