"""change_default_value_in_energy_table

Revision ID: 770d920ee889
Revises: 8ab1d5bd6b59
Create Date: 2025-07-21 20:08:49.154665

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '770d920ee889'
down_revision: Union[str, None] = '8ab1d5bd6b59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'energies',
        'recharge_time',
        existing_type=sa.Integer(),
        server_default='15',  # Nuevo valor por defecto
        nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        'energies',
        'recharge_time',
        existing_type=sa.Integer(),
        server_default='30',  # Valor original
        nullable=False
    )
    pass
