"""merge_branches

Revision ID: 056dc2723767
Revises: cf02b2692aff, d5763304f4a7
Create Date: 2025-08-07 19:08:42.573246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '056dc2723767'
down_revision: Union[str, None] = ('cf02b2692aff', 'd5763304f4a7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
