"""merge heads

Revision ID: 113b2cb4df9a
Revises: cf02b2692aff, d5763304f4a7
Create Date: 2025-08-06 17:23:53.452114

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '113b2cb4df9a'
down_revision: Union[str, None] = ('cf02b2692aff', 'd5763304f4a7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
