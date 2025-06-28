from uuid import UUID
from pydantic import BaseModel
from pydantic.alias_generators import to_camel
from app.api.users.user_schema import UserSchema, UserCreateSchema, UserResponseSchema


class PatientSchema(UserSchema):
    pass


class PatientCreateSchema(UserCreateSchema):
    pass


class PatientResponseSchema(UserResponseSchema):
    patient_id: UUID
