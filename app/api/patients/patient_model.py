from typing import Optional, List
from uuid import UUID
from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel


class PatientModel(BaseNayaModel, table=True):
    __tablename__ = "patients"

    user_id: UUID = Field(default=None, foreign_key="users.id")
    is_connected: bool = Field(default=False)
    animal_id: Optional[UUID] = Field(default=None, foreign_key="animals.id")

    user: "UserModel" = Relationship(back_populates="patient")  # type: ignore
    animal: "AnimalModel" = Relationship(back_populates="patients")  # type: ignore
    connections: List["ConnectionModel"] = Relationship(back_populates="patient")  # type: ignore
