"""Merge_connection_verification_resete_codes

Revision ID: e1a063bf86b1
Revises: 021f1181bb6d, 40325f49d943
Create Date: 2025-06-28 03:16:14.646996

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1a063bf86b1'
down_revision: Union[str, None] = ('021f1181bb6d', '40325f49d943')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
