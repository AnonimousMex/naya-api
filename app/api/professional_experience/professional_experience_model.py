from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from app.core.base_model import BaseNayaModel

if TYPE_CHECKING:
    from app.api.therapists.therapist_model import TherapistModel


class ProfessionalExperienceModel(BaseNayaModel, table=True):
    __tablename__ = "professional_experience"

    id_therapist: UUID = Field(foreign_key="therapist.id", nullable=False)
    institute: str = Field(max_length=200, nullable=False)
    position: str = Field(max_length=100, nullable=False)
    period: str = Field(max_length=50, nullable=False)
    activity: Optional[str] = Field(max_length=500, default=None)

    # Relationships - temporarily commented to avoid circular import issues
    # therapist: "TherapistModel" = Relationship(back_populates="professional_experiences")
