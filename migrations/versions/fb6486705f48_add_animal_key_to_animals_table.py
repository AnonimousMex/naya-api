"""add animal_key to animals table

Revision ID: fb6486705f48
Revises: 73d319f65f5b
Create Date: 2025-07-09 00:59:39.284671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fb6486705f48'
down_revision: Union[str, None] = '73d319f65f5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column('animals', sa.Column('animal_key', sa.String(length=50), nullable=True))
    op.execute("UPDATE animals SET animal_key = lower(name)")
    op.alter_column('animals', 'animal_key', nullable=False)


def downgrade() -> None:
    op.drop_column('animals', 'animal_key')
