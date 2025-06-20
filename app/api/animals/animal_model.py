from typing import List
from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel


class AnimalModel(BaseNayaModel, table=True):
    __tablename__ = "animals"

    name: str = Field(default=None)
    description: str = Field(default=None)

    patients: List["PatientModel"] = Relationship(back_populates="animal")  # type: ignore
