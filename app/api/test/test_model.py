from datetime import datetime
from uuid import UUID

from typing import List, Optional
from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel


class TestModel(BaseNayaModel, table=True):
    __tablename__="tests"

    user_id: UUID = Field(foreign_key="users.id", nullable=False)

    # Resultado de actividad realizada por el niño. Nullable para no romper
    # tests creados antes de la feature de activity-results.
    activity_id: Optional[UUID] = Field(default=None, foreign_key="activities.id")
    score: Optional[int] = Field(default=None)
    duration_seconds: Optional[int] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    user: "UserModel" = Relationship(back_populates="test")  # type: ignore
    emotion_results: List["EmotionResultsModel"] = Relationship(back_populates="test") # type: ignore
    testAnswer: List["TestAnswerModel"] = Relationship(back_populates="test") # type: ignore
    testVeredict: List["TestVeredictModel"] = Relationship(back_populates="test") # type: ignore
