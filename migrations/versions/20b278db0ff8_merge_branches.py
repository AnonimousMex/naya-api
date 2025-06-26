"""merge_branches

Revision ID: 20b278db0ff8
Revises: 3aeab2956e96, 4a4c5e63288c
Create Date: 2025-06-26 05:46:49.397872

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20b278db0ff8'
down_revision: Union[str, None] = ('3aeab2956e96', '4a4c5e63288c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
