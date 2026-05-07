"""add activity-results metrics columns and parent_child table

Revision ID: a1b2c3d4e5f6
Revises: e193060ca1c1
Create Date: 2026-05-06 22:00:00.000000

Cambios:
- tests: +score, +duration_seconds, +completed_at, +activity_id (FK opcional)
- test_answer: +emotion_intensity, +coping_category
- questions: +trigger_category
- parent_child: nueva tabla (rel tutor↔paciente)

Todos los campos nuevos en tablas existentes son nullable para no romper datos
históricos.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel  # noqa: F401


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "e193060ca1c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # añadir 'PARENT' al enum SQL userroles2 (sólo si no existe)
    op.execute(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel='PARENT' "
        "AND enumtypid = (SELECT oid FROM pg_type WHERE typname='userroles2')) "
        "THEN ALTER TYPE userroles2 ADD VALUE 'PARENT'; "
        "END IF; END $$;"
    )

    # tests: campos de actividad
    op.add_column(
        "tests",
        sa.Column("activity_id", sa.Uuid(), nullable=True),
    )
    op.add_column("tests", sa.Column("score", sa.Integer(), nullable=True))
    op.add_column("tests", sa.Column("duration_seconds", sa.Integer(), nullable=True))
    op.add_column("tests", sa.Column("completed_at", sa.DateTime(), nullable=True))
    op.create_foreign_key(
        "fk_tests_activity_id",
        "tests",
        "activities",
        ["activity_id"],
        ["id"],
    )

    # test_answer: intensidad + coping
    op.add_column(
        "test_answer", sa.Column("emotion_intensity", sa.Integer(), nullable=True)
    )
    op.add_column(
        "test_answer",
        sa.Column(
            "coping_category", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True
        ),
    )

    # questions: trigger
    op.add_column(
        "questions",
        sa.Column(
            "trigger_category",
            sqlmodel.sql.sqltypes.AutoString(length=20),
            nullable=True,
        ),
    )

    # parent_child: relación tutor↔niño
    op.create_table(
        "parent_child",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("parent_user_id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["parent_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "parent_user_id", "patient_id", name="uq_parent_child_pair"
        ),
    )


def downgrade() -> None:
    op.drop_table("parent_child")
    op.drop_column("questions", "trigger_category")
    op.drop_column("test_answer", "coping_category")
    op.drop_column("test_answer", "emotion_intensity")
    op.drop_constraint("fk_tests_activity_id", "tests", type_="foreignkey")
    op.drop_column("tests", "completed_at")
    op.drop_column("tests", "duration_seconds")
    op.drop_column("tests", "score")
    op.drop_column("tests", "activity_id")
