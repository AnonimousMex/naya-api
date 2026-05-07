"""
Conftest mínimo. Las fixtures que crean filas sintéticas para MetricsService
viven aquí para reutilizarse entre módulos de tests.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest


def _row(emotion_name: str, *, answer_text: str = "txt", coping=None, trigger=None,
         created_at: datetime | None = None):
    """
    Construye una tupla (TestAnswer, Answer, Question, Emotion, Test) con
    SimpleNamespace — sin tocar SQLAlchemy ni la BD.
    """
    return (
        SimpleNamespace(coping_category=coping, emotion_intensity=70),
        SimpleNamespace(answer_text=answer_text, emotion_id=uuid4()),
        SimpleNamespace(trigger_category=trigger),
        SimpleNamespace(name=emotion_name),
        SimpleNamespace(created_at=created_at or datetime(2026, 5, 1, 12, tzinfo=timezone.utc)),
    )


@pytest.fixture
def make_row():
    """Fábrica reutilizable para tests del MetricsService."""
    return _row
