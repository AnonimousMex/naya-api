
from uuid import UUID
from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel


class SituationModel( BaseNayaModel, table=True):
    __tablename__="situations"

    title: str = Field(nullable=False)
    story: str = Field(max_length=500, nullable=False)
    emotion_id: UUID = Field(foreign_key="emotions.id" ,nullable=False)

    emotion: "EmotionModel" = Relationship(back_populates="situations") # type: ignore

