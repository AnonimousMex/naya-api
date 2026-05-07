import jwt
import time
import logging
from uuid import UUID
from datetime import datetime, timezone, timedelta

from typing import Optional
from passlib.context import CryptContext

from app.core.settings import settings

from app.constants.user_constants import UserRoles

from app.models.user_model import UserModel

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
        if token and token.lower().startswith("bearer "):
            token = token.split(" ", 1)[1].strip()
        token_data = jwt.decode(
            jwt=token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return token_data

    except jwt.PyJWTError as e:
        logging.error(e)
        return None


def get_user_id_from_token(token: str) -> str:
    """
    Decodifica el token y devuelve `user_id` (campo `sub` del JWT).
    Lanza HTTPException 401 si el token es inválido, expirado o no trae sub.
    Acepta tanto el JWT puro como el header `Bearer <jwt>`.
    """
    from fastapi import HTTPException, status

    decoded = decode_token(token)
    if not decoded or not decoded.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return decoded["sub"]


def get_user_token(
    user: UserModel,
    user_type: UserRoles,
    is_refresh: bool,
    patient_or_therapist_id: Optional[UUID],
) -> str:
    animal_id = None
    code_connection = None

    if user_type == UserRoles.PATIENT.value and hasattr(user, "patient") and user.patient:
        animal_id = str(user.patient.animal_id) if user.patient.animal_id else None

    if user_type == UserRoles.THERAPIST.value and hasattr(user, "therapist") and user.therapist:
        code_connection = user.therapist.code_conection

    user_data = {
        "email": user.email,
        "user_id": str(user.id),
        "name": user.name,
        "user_type": user_type,
    }
    # Sólo terapeuta/paciente llevan id específico de rol; el tutor (PARENT) no.
    if patient_or_therapist_id is not None:
        if user_type == UserRoles.PATIENT.value:
            user_data["patient_id"] = str(patient_or_therapist_id)
        elif user_type == UserRoles.THERAPIST.value:
            user_data["therapist_id"] = str(patient_or_therapist_id)
    if animal_id is not None:
        user_data["animal_id"] = animal_id

    if code_connection is not None:
        user_data["code_connection"] = code_connection

    return create_access_token(
        user_data=user_data,
        expires_delta=timedelta(days=2) if is_refresh else timedelta(hours=1),
        refresh_token=is_refresh,
    )
