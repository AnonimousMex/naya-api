"""merge_heads_infoAll_badges

Revision ID: e193060ca1c1
Revises: 9a3962479f57, fa1d2c3b0025
Create Date: 2025-08-12 06:35:55.018844

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e193060ca1c1'
down_revision: Union[str, None] = ('9a3962479f57', 'fa1d2c3b0025')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
