from uuid import UUID
from pydantic import BaseModel
from typing import List


class SpecialtyBase(BaseModel):
    name: str


class SpecialtyCreate(SpecialtyBase):
    pass


class SpecialtyResponse(SpecialtyBase):
    id: UUID

    class Config:
        from_attributes = True


class TherapistSpecialtyAssign(BaseModel):
    therapist_id: UUID
    specialty_ids: List[UUID]
