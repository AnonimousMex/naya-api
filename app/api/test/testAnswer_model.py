from uuid import UUID

from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel


class TestAnswerModel(BaseNayaModel, table=True):
    __tablename__= "test_answer"

    test_id: UUID = Field(foreign_key="tests.id", nullable=False)
    answer_id: UUID = Field(foreign_key="answers.id", nullable=False)

    test: "TestModel" = Relationship(back_populates="testAnswer") # type: ignore
    answer: "AnswerModel" = Relationship(back_populates="testAnswer") # type: ignore