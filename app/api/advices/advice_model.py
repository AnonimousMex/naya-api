from typing import List
from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel


class AdviceModel(BaseNayaModel, table=True):
    __tablename__="advices"

    title: str = Field(max_length=20, nullable=False)
    description: str = Field(max_length=80, nullable=False)

    advices_shown: List["AdvicesShownModel"] = Relationship(back_populates="advice")  # type: ignore