from uuid import UUID

from typing import List
from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel


class TestModel(BaseNayaModel, table=True):
    __tablename__="tests"

    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    
    user: "UserModel" = Relationship(back_populates="test")  # type: ignore
    emotion_results: List["EmotionResultsModel"] = Relationship(back_populates="test") # type: ignore
    testAnswer: List["TestAnswerModel"] = Relationship(back_populates="test") # type: ignore
    testVeredict: List["TestVeredictModel"] = Relationship(back_populates="test") # type: ignore