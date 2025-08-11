"""create_professional_experience_table

Revision ID: 3c4d5e6f7a8b
Revises: 2b3c4d5e6f7a
Create Date: 2025-08-09 12:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '3c4d5e6f7a8b'
down_revision: Union[str, None] = '2b3c4d5e6f7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # Crear tabla professional_experience
    op.create_table('professional_experience',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('id_therapist', sa.Uuid(), nullable=False),
        sa.Column('institute', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
        sa.Column('position', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('period', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('activity', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        sa.ForeignKeyConstraint(['id_therapist'], ['therapist.id'], name='fk_professional_experience_therapist'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('professional_experience')
