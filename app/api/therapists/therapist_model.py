from uuid import UUID

from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel

class TherapistModel(BaseNayaModel, table=True):
    __tablename__= "therapist"

    user_id: UUID = Field(default=None, foreign_key="users.id")
    description: str = Field(default=None)
    phone: str = Field(default=None)
    street: str = Field(default=None)
    city: str = Field(default=None)
    state: str = Field(default=None)
    postal_code: str = Field(default=None)
    code_conection: str = Field(default=None)
    user: "UserModel" = Relationship(back_populates="therapist")  # type: ignore