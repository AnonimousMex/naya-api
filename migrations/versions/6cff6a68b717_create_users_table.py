"""create_users_table

Revision ID: 6cff6a68b717
Revises: 
Create Date: 2025-06-19 15:59:33.589521

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '6cff6a68b717'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('users',
    sa.Column("id", sa.Uuid(), nullable=False),
    sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column("email", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False),
    sa.Column("password", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False),
    sa.Column(
           "user_kind",
           sa.Enum("PATIENT", "THERAPIST", name="userroles2"),
           nullable=False,
       ),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('users')
