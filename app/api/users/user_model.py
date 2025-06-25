from datetime import date
from typing import Optional, List

from sqlmodel import Field, Relationship
from pydantic import EmailStr

from app.core.base_model import BaseNayaModel

from app.utils.regex import Regex

from app.constants.user_constants import UserRoles


class UserModel(BaseNayaModel, table=True):
    __tablename__ = "users"

    name: str = Field(min_length=4, max_length=20, regex=Regex.LETTERS)
    email: EmailStr = Field(min_length=4, max_length=40, unique=True)
    password: str = Field(min_length=8, exclude=True)
    is_verified: bool = Field(default=False)
    user_kind: UserRoles

    patient: Optional["PatientModel"] = Relationship(back_populates="user")  # type: ignore
    verification_code: "VerificationCodeModel" = Relationship(back_populates="user")  # type: ignore
    # therapist: Optional["TherapistModel"] = Relationship(back_populates="user")  # type: ignore
    # verification_code: "VerificationCodeModel" = Relationship(back_populates="user")  # type: ignore
    # verification_codes_password_reset: "VerificationCodePasswordResetModel" = Relationship(back_populates="user")  # type: ignore
