from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from pydantic.alias_generators import to_camel

from app.core.mixins.password_validation_mixin import PasswordValidationMixin

from app.utils.regex import Regex


class UserSchema(BaseModel):
    name: str = Field(min_length=4, max_length=20, pattern=Regex.USER_NAME)
    email: EmailStr = Field(max_length=40)

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        from_attributes = True


class UserCreateSchema(UserSchema, PasswordValidationMixin):
    pass

    class Config:
        extra = "forbid"


class UserResponseSchema(UserSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime
