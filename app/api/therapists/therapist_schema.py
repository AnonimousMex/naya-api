

from uuid import UUID
from app.api.users.user_schema import UserCreateSchema, UserResponseSchema, UserSchema
from pydantic import BaseModel
from datetime import date, time, timezone


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


