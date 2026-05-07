from typing import List, Optional
from pydantic import BaseModel


class AnimalSchema(BaseModel):
    name: Optional[str] = None
    color_ui: Optional[str] = None
    animal_key: Optional[str] = None


class ChildSchema(BaseModel):
    patient_id: str
    name: str
    email: str
    animal: Optional[AnimalSchema] = None


class SpecialtySchema(BaseModel):
    name: str
    description: Optional[str] = None

class TherapistSchema(BaseModel):
    therapist_id: str
    name: str
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    specialties: Optional[List[SpecialtySchema]] = []
    experiences: Optional[List[dict]] = []

class ListTherapistsResponse(BaseModel):
    therapists: List[TherapistSchema]
