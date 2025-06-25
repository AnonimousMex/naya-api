from typing import Optional
from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship
from app.core.base_model import BaseNayaModel

from app.api.pictures.picture_model import PictureModel
from app.api.animals.animal_model import AnimalModel
from app.api.emotions.emotion_model import EmotionModel


class PictureAnimalEmotionModel(BaseNayaModel, table=True):
    __tablename__ = "picture_animal_emotion"

    id_picture: UUID = Field(foreign_key="pictures.id", nullable=False)
    id_animal: UUID = Field(foreign_key="animals.id", nullable=False)
    id_emotion: UUID = Field(foreign_key="emotions.id", nullable=False)

    picture: Optional["PictureModel"] = Relationship(back_populates="animal_emotions")  # type: ignore
    animal: Optional["AnimalModel"] = Relationship(back_populates="picture_emotions")  # type: ignore
    emotion: Optional["EmotionModel"] = Relationship(back_populates="picture_animals")  # type: ignore
