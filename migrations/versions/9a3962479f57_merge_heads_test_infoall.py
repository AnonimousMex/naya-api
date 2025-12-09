"""merge_heads_test_infoAll

Revision ID: 9a3962479f57
Revises: 3c4d5e6f7a8b, 7355f2f3fe5c
Create Date: 2025-08-12 06:05:45.059661

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a3962479f57'
down_revision: Union[str, None] = ('3c4d5e6f7a8b', '7355f2f3fe5c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
