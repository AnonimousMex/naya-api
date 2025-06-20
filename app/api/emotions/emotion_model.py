from typing import List
from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel


class EmotionModel(BaseNayaModel, table=True):
    __tablename__ = "emotions"

    name: str = Field(index=True, nullable=False)
