"""create_specialty_therapist_table

Revision ID: 2b3c4d5e6f7a
Revises: 1a2b3c4d5e6f
Create Date: 2025-08-09 12:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '2b3c4d5e6f7a'
down_revision: Union[str, None] = '1a2b3c4d5e6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # Crear tabla de relación specialty_therapist
    op.create_table('specialty_therapist',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('id_therapist', sa.Uuid(), nullable=False),
        sa.Column('id_specialty', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        sa.ForeignKeyConstraint(['id_therapist'], ['therapist.id'], name='fk_specialty_therapist_therapist'),
        sa.ForeignKeyConstraint(['id_specialty'], ['specialties.id'], name='fk_specialty_therapist_specialty'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id_therapist', 'id_specialty', name='uq_therapist_specialty')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('specialty_therapist')
