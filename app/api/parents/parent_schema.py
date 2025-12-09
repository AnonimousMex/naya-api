from typing import List, Optional
from pydantic import BaseModel

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
