from sqlmodel import Field
from app.core.base_model import BaseNayaModel
from sqlmodel import Relationship
from typing import List


class PictureModel(BaseNayaModel, table=True):
    __tablename__ = "pictures"

    picture: str = Field(nullable=False)
    is_profile: bool = Field(default=False)

    animal_emotions: List["PictureAnimalEmotionModel"] = Relationship(back_populates="picture")  # type: ignore
