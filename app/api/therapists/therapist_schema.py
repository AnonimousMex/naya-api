from uuid import UUID

from pydantic import BaseModel
from app.api.users.user_schema import UserCreateSchema, UserResponseSchema, UserSchema
from datetime import date, time, timezone
from pydantic.alias_generators import to_camel

class TherapistSchema(UserSchema):
    pass


class TherapistCreateSchema(UserCreateSchema):
    pass


class TherapistResponseSchema(UserResponseSchema):
    therapist_id: UUID

class AppointmentRequest(BaseModel):
    patient_id: UUID
    date: date
    time: time

class AppointmentResponse(BaseModel):
    therapist_id: UUID
    patient_id: UUID
    date: date
    time: time

class EditAppointmentRequest(BaseModel):
    appointment_id: UUID

class AppointmentListResponse(BaseModel):
    id: UUID
    patient_id: UUID
    date: date
    time: time

class AppointmentListRequest(BaseModel):
    token: str
    
class RescheduleAppointmentRequest(BaseModel):
    appointment_id: UUID
    date: date
    time: time

class DisconnectPatientRequest(BaseModel):
    id_patient: UUID

    class Config:
        alias_generator = to_camel
        populate_by_name = True

# Schema para listar terapeutas (solo id y nombre)
class TherapistListResponseSchema(BaseModel):
    therapist_id: UUID
    name: str

