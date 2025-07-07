from typing import List
from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel


class AnimalModel(BaseNayaModel, table=True):
    __tablename__ = "animals"

    name: str = Field(default=None)
    description: str = Field(default=None)
    color_ui: str = Field(default="#FFFFFF", max_length=7)

    patients: List["PatientModel"] = Relationship(back_populates="animal")  # type: ignore
    picture_emotions: List["PictureAnimalEmotionModel"] = Relationship(back_populates="animal")  # type: ignore
