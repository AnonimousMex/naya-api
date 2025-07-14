import jwt
import time
import logging
from uuid import UUID
from datetime import datetime, timezone, timedelta

from typing import Optional
from passlib.context import CryptContext

from app.core.settings import settings

from app.constants.user_constants import UserRoles

from app.api.users.user_model import UserModel

ACCESS_TOKEN_EXPIRY = 3600

password_context = CryptContext(schemes=["bcrypt"])


def get_password_hash(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_access_token(
    user_data: dict, expires_delta: timedelta = None, refresh_token: bool = False
) -> str:
    payload = {}
    payload["sub"] = user_data["user_id"]
    payload["user"] = user_data
    payload["exp"] = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    payload["iat"] = int(time.time())
    payload["refresh"] = refresh_token

    token = jwt.encode(
        payload=payload, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    return token


def decode_token(token: str) -> Optional[dict]:
    try:
        token_data = jwt.decode(
            jwt=token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return token_data

    except jwt.PyJWTError as e:
        logging.error(e)
        return None


def get_user_token(
    user: UserModel,
    user_type: UserRoles,
    is_refresh: bool,
    patient_or_therapist_id: UUID,
) -> str:
    custom_id_key_name = (
        "patient_id" if user_type == UserRoles.PATIENT.value else "therapist_id"
    )
    animal_id = None
    if user_type == UserRoles.PATIENT.value and hasattr(user, "patient") and user.patient:
        animal_id = str(user.patient.animal_id) if user.patient.animal_id else None

    user_data = {
        "email": user.email,
        "user_id": str(user.id),
        "name": user.name,
        "user_type": user_type,
        custom_id_key_name: str(patient_or_therapist_id),
    }
    if animal_id is not None:
        user_data["animal_id"] = animal_id

    return create_access_token(
        user_data=user_data,
        expires_delta=timedelta(days=2) if is_refresh else timedelta(hours=1),
        refresh_token=is_refresh,
    )
