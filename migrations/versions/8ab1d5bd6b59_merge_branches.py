"""merge branches

Revision ID: 8ab1d5bd6b59
Revises: 1577b1cd78c5, 60469f5a2efc
Create Date: 2025-07-21 20:08:25.659534

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ab1d5bd6b59'
down_revision: Union[str, None] = ('1577b1cd78c5', '60469f5a2efc')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
