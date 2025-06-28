"""create_therapists_table

Revision ID: 4a4c5e63288c
Revises: 1d4418412945
Create Date: 2025-06-22 06:04:38.619976

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '4a4c5e63288c'
down_revision: Union[str, None] = '1d4418412945'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.create_table('therapist',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=True),
    sa.Column('phone', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
    sa.Column('street', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
    sa.Column('city', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
    sa.Column('state', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
    sa.Column('postal_code', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
    sa.Column('code_conection', sqlmodel.sql.sqltypes.AutoString(length=4), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),

    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_therapist_user' ),
    sa.PrimaryKeyConstraint('id'),

    sa.UniqueConstraint('code_conection', name='uq_therapist_code')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('therapist')
