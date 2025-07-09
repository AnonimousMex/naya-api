from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from pydantic.alias_generators import to_camel


class VerificationRequest(BaseModel):
    code: str

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class RequestPasswordChange(BaseModel):
    email: EmailStr = Field(max_length=40)

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class ResendCode(BaseModel):
    email: EmailStr = Field(max_length=40)

    class config:
        alias_generator = to_camel
        populate_by_name = True


class SelectProfileRequest(BaseModel):
    user_id: UUID
    id_animal: UUID

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class ConnectionCodeRequest(BaseModel):
    id_patient: UUID
    code: str

    class Config:
        alias_generator = to_camel
        populate_by_name = True
