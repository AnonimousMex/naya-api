from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from app.core.base_model import BaseNayaModel

if TYPE_CHECKING:
    from app.api.therapists.therapist_model import TherapistModel


class SpecialtyModel(BaseNayaModel, table=True):
    __tablename__ = "specialties"

    name: str = Field(max_length=100, nullable=False, unique=True)
    deleted_at: Optional[str] = Field(default=None)


class SpecialtyTherapistModel(BaseNayaModel, table=True):
    __tablename__ = "specialty_therapist"

    id_therapist: UUID = Field(foreign_key="therapist.id", nullable=False)
    id_specialty: UUID = Field(foreign_key="specialties.id", nullable=False)
