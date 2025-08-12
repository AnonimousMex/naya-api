from uuid import UUID
from typing import List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel
from datetime import date, time, datetime
from typing import Optional

if TYPE_CHECKING:
    from app.api.specialties.specialty_model import SpecialtyModel
    from app.api.professional_experience.professional_experience_model import ProfessionalExperienceModel


class TherapistModel(BaseNayaModel, table=True):
    __tablename__ = "therapist"

    user_id: UUID = Field(default=None, foreign_key="users.id")
    description: str = Field(default=None)
    phone: str = Field(default=None)
    street: str = Field(default=None)
    city: str = Field(default=None)
    state: str = Field(default=None)
    postal_code: str = Field(default=None)
    code_conection: str = Field(default=None)

    user: "UserModel" = Relationship(back_populates="therapist")  # type: ignore
    connections: List["ConnectionModel"] = Relationship(back_populates="therapist")  # type: ignore
    
    # Relaciones agregadas después de crear las migraciones
    # specialties: List["SpecialtyModel"] = Relationship(back_populates="therapists")
    # professional_experiences: List["ProfessionalExperienceModel"] = Relationship(back_populates="therapist")

class AppointmentModel(BaseNayaModel, table=True):
    __tablename__ = "appointments"

    therapist_id: UUID = Field(foreign_key="therapist.id")
    patient_id: UUID = Field(foreign_key="patients.id")
    date: date
    time: time
    status: bool = Field(default=True)
    deleted_at: Optional[datetime] = Field(default=None)


