from uuid import UUID
from typing import Optional
from datetime import datetime, timedelta, timezone

from sqlmodel import Field, Relationship

from app.core.base_model import BaseNayaModel


class BaseVerificationCodeModel(BaseNayaModel):
    code: str = Field(unique=True)
    is_alive: bool = Field(default=True)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=2)
    )
    user_id: Optional[UUID] = Field(default=None, foreign_key="users.id")


class VerificationCodeModel(BaseVerificationCodeModel, table=True):
    __tablename__ = "verification_codes"

    user: "UserModel" = Relationship(back_populates="verification_code")  # type: ignore


class ConnectionModel(BaseNayaModel, table=True):
    __tablename__ = "connections"

    therapist_id: UUID = Field(foreign_key="therapist.id")
    patient_id: UUID = Field(foreign_key="patients.id")

    therapist: "TherapistModel" = Relationship(back_populates="connections")  # type: ignore
    patient: "PatientModel" = Relationship(back_populates="connections")  # type: ignore
