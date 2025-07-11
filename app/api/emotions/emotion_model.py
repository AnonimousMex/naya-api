from typing import List
from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel


class EmotionModel(BaseNayaModel, table=True):
    __tablename__ = "emotions"

    name: str = Field(index=True, nullable=False)

    picture_animals: List["PictureAnimalEmotionModel"] = Relationship(back_populates="emotion")  # type: ignore
    descriptions: List["EmotionDescriptionModel"] = Relationship(back_populates="emotion") # type: ignore
    situations: List["SituatioMOdel"] = Relationship(back_populates="emotion") # type: ignore
