"""merge branches

Revision ID: 60469f5a2efc
Revises: 01ac87f73f08, fb6486705f48
Create Date: 2025-07-11 23:54:28.107339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60469f5a2efc'
down_revision: Union[str, None] = ('01ac87f73f08', 'fb6486705f48')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
