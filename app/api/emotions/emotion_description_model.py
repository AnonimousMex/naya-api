# from uuid import UUID
# from sqlmodel import Field, Relationship
# from app.core.base_model import BaseNayaModel


# class EmotionDescriptionModel(BaseNayaModel, table=True):
#     __tablename__ = "emotion_descriptions"

#     emotion_id: UUID = Field(foreign_key="emotions.id", nullable=False)
#     description: str = Field(nullable=False)

#     emotion: Optional["EmotionModel"] = Relationship(back_populates="descriptions")  # type: ignore
