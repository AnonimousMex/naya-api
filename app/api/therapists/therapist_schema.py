from uuid import UUID

from pydantic import BaseModel
from app.api.users.user_schema import UserCreateSchema, UserResponseSchema, UserSchema
from pydantic.alias_generators import to_camel


class TherapistSchema(UserSchema):
    pass


class TherapistCreateSchema(UserCreateSchema):
    pass


class TherapistResponseSchema(UserResponseSchema):
    therapist_id: UUID


class DisconnectPatientRequest(BaseModel):
    id_patient: UUID
    id_therapist: UUID  # si obtienes el terapeuta del token, elimínalo

    class Config:
        alias_generator = to_camel
        populate_by_name = True
