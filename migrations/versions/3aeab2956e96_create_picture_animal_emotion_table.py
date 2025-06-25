"""create_picture_animal_emotion_table

Revision ID: 3aeab2956e96
Revises: c1bb91479aa5
Create Date: 2025-06-20 22:46:58.245260

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "3aeab2956e96"
down_revision: Union[str, None] = "c1bb91479aa5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "picture_animal_emotion",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("id_picture", sa.Uuid(), nullable=False),
        sa.Column("id_animal", sa.Uuid(), nullable=False),
        sa.Column("id_emotion", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_picture"], ["pictures.id"], name="fk_picture_emotion_picture"
        ),
        sa.ForeignKeyConstraint(
            ["id_animal"], ["animals.id"], name="fk_picture_emotion_animal"
        ),
        sa.ForeignKeyConstraint(
            ["id_emotion"], ["emotions.id"], name="fk_picture_emotion_emotion"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_picture_animal_emotion_id_picture"),
        "picture_animal_emotion",
        ["id_picture"],
        unique=False,
    )
    op.create_index(
        op.f("ix_picture_animal_emotion_id_animal"),
        "picture_animal_emotion",
        ["id_animal"],
        unique=False,
    )
    op.create_index(
        op.f("ix_picture_animal_emotion_id_emotion"),
        "picture_animal_emotion",
        ["id_emotion"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_picture_animal_emotion_id_emotion"),
        table_name="picture_animal_emotion",
    )
    op.drop_index(
        op.f("ix_picture_animal_emotion_id_animal"), table_name="picture_animal_emotion"
    )
    op.drop_index(
        op.f("ix_picture_animal_emotion_id_picture"),
        table_name="picture_animal_emotion",
    )
    op.drop_table("picture_animal_emotion")
