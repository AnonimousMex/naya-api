
from typing import List, Optional
from uuid import UUID
from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel


class EmotionModel(BaseNayaModel, table=True):
    __tablename__ = "emotions"

    id: Optional[UUID] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)

    picture_animals: List["PictureAnimalEmotionModel"] = Relationship(back_populates="emotion")  # type: ignore
    descriptions: List["EmotionDescriptionModel"] = Relationship(back_populates="emotion")  # type: ignore
    situations: List["SituationModel"] = Relationship(back_populates="emotion")  # type: ignore
    emotion_results: List["EmotionResultsModel"] = Relationship(back_populates="emotion") # type: ignore
    story: List["StoryModel"] = Relationship(back_populates="emotion") # type: ignore
    answer: List["AnswerModel"] = Relationship(back_populates="emotion") # type: ignore
    veredict: List["VeredictModel"] = Relationship(back_populates="emotion") # type: ignore

class EmotionDescriptionModel(BaseNayaModel, table=True):
    __tablename__ = "emotion_descriptions"

    id: Optional[UUID] = Field(default=None, primary_key=True)
    emotion_id: UUID = Field(foreign_key="emotions.id", nullable=False)
    description: str = Field(nullable=False)

    emotion: EmotionModel = Relationship(back_populates="descriptions")  # type: ignore

class SituationModel(BaseNayaModel, table=True):
    __tablename__="situations"

    title: str = Field(nullable=False)
    story: str = Field(max_length=500, nullable=False)
    emotion_id: UUID = Field(foreign_key="emotions.id" ,nullable=False)
    image_url: str = Field(nullable=True, default=None)

    emotion: EmotionModel = Relationship(back_populates="situations") # type: ignore

class EmotionResultsModel(BaseNayaModel, table=True):
    __tablename__= "emotion_results"

    test_id: UUID = Field(foreign_key="tests.id", nullable=False)
    emotion_id: UUID = Field(foreign_key="emotions.id", nullable=False)
    percentage: float = Field(default=0.0, ge=0.0, le=100.0)

    emotion: EmotionModel = Relationship(back_populates="emotion_results") # type: ignore
    test: "TestModel" = Relationship(back_populates="emotion_results") # type: ignore

class StoryModel(BaseNayaModel, table=True):
    __tablename__= "stories"

    title: str = Field( max_length= 120, nullable=False)
    stage_1: str =Field (max_length= 100, nullable=False)
    stage_2: str =Field (max_length= 100, nullable=False)
    image_url: str = Field(nullable=False)
    emotion_id: UUID = Field(foreign_key="emotions.id", nullable=False)

    emotion: EmotionModel = Relationship(back_populates="story") # type: ignore
    question: List["QuestionModel"] = Relationship(back_populates="story") # type: ignore

class AnswerModel(BaseNayaModel, table=True):
    __tablename__= "answers"

    question_id: UUID = Field(foreign_key="questions.id", nullable=False)
    answer_text: str = Field(max_length=150, nullable=False)
    emotion_id: UUID = Field(foreign_key="emotions.id", nullable=False)
    score: int = Field(nullable=False)

    question: "QuestionModel" = Relationship(back_populates="answer") # type: ignore
    emotion: EmotionModel = Relationship(back_populates="answer") # type: ignore
    testAnswer: List["TestAnswerModel"] = Relationship(back_populates="answer") # type: ignore

class TestAnswerModel(BaseNayaModel, table=True):
    __tablename__= "test_answer"

    test_id: UUID = Field(foreign_key="tests.id", nullable=False)
    answer_id: UUID = Field(foreign_key="answers.id", nullable=False)

    test: "TestModel" = Relationship(back_populates="testAnswer") # type: ignore
    answer: "AnswerModel" = Relationship(back_populates="testAnswer") # type: ignore
class VeredictModel(BaseNayaModel, table=True):
    __tablename__= "veredicts"

    emotion_id: UUID = Field(foreign_key="emotions.id", nullable=False)
    min_range: float = Field(nullable=False)
    max_range: int = Field(nullable=False)
    veredict: str = Field(nullable=False)

    emotion: EmotionModel = Relationship(back_populates="veredict") # type: ignore
    testVeredict: List["TestVeredictModel"] = Relationship(back_populates="veredict") # type: ignore

class TestVeredictModel(BaseNayaModel, table=True):
    __tablename__= "test_veredict"

    test_id: UUID = Field(foreign_key="tests.id", nullable=False)
    veredict_id: UUID = Field(foreign_key="veredicts.id", nullable=False)

    test: "TestModel" = Relationship(back_populates="testVeredict") # type: ignore
    veredict: "VeredictModel" = Relationship(back_populates="testVeredict") # type: ignore