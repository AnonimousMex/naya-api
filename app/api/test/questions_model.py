from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel


class QuestionModel(BaseNayaModel, table=True):
    __tablename__= "questions"

    story_id: UUID = Field(foreign_key="stories.id", nullable=False)
    question: str = Field(max_length=150, nullable= False)
    # Categoría del disparador emocional asociado a esta pregunta
    # (self/siblings/friends/father/mother/teachers). Nullable.
    trigger_category: Optional[str] = Field(default=None, max_length=20)

    story: "StoryModel" = Relationship(back_populates="question") # type: ignore
    answer: List["AnswerModel"] = Relationship(back_populates="question") # type: ignore
