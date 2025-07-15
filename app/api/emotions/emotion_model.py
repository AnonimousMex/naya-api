
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

    emotion: EmotionModel = Relationship(back_populates="situations") # type: ignore

