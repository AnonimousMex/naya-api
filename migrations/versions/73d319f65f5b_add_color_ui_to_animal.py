"""add color_ui to animal

Revision ID: 73d319f65f5b
Revises: e1a063bf86b1
Create Date: 2025-07-07 07:40:29.901327

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '73d319f65f5b'
down_revision: Union[str, None] = 'e1a063bf86b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('animals', sa.Column('color_ui', sa.String(length=7), nullable=False, server_default="#BEBEBE"))
    op.alter_column('animals', 'color_ui', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('animals', 'color_ui')
