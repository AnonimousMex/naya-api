"""merge_create_therapists_and_picture_animal_emotion

Revision ID: b46ee37d7bcf
Revises: 3aeab2956e96, 4a4c5e63288c
Create Date: 2025-06-27 17:28:07.014697

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b46ee37d7bcf'
down_revision: Union[str, None] = ('3aeab2956e96', '4a4c5e63288c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
