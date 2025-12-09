from uuid import UUID
from pydantic import BaseModel
from typing import Optional


class ProfessionalExperienceBase(BaseModel):
    institute: str
    position: str
    period: str
    activity: Optional[str] = None


class ProfessionalExperienceCreate(ProfessionalExperienceBase):
    id_therapist: UUID


class ProfessionalExperienceUpdate(BaseModel):
    institute: Optional[str] = None
    position: Optional[str] = None
    period: Optional[str] = None
    activity: Optional[str] = None


class ProfessionalExperienceResponse(ProfessionalExperienceBase):
    id: UUID
    id_therapist: UUID

    class Config:
        from_attributes = True
