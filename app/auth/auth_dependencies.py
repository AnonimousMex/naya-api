# app/api/auth/auth_dependencies.py
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from typing import Optional
from uuid import UUID
import jwt
import os

from sqlmodel import Session, select
from app.core.settings import settings
from app.core.database import engine  # asegúrate de tener un engine centralizado
from app.api.therapists.therapist_model import TherapistModel
from app.api.patients.patient_model import PatientModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # solo para Swagger

SUPABASE_SECRET = settings.SUPABASE_JWT_SECRET or os.getenv("SUPABASE_JWT_SECRET", "")

def _decode_supabase_jwt(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            SUPABASE_SECRET,
            algorithms=["HS256"],
            audience="authenticated",  # Supabase
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> UUID:
    payload = _decode_supabase_jwt(token)
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Token without 'sub'")
    try:
        return UUID(sub)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid 'sub' format")

def get_session():
    with Session(engine) as session:
        yield session

def get_current_therapist_id(
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> UUID:
    stmt = select(TherapistModel).where(TherapistModel.user_id == user_id)
    therapist = session.exec(stmt).first()
    if not therapist:
        # Si tu lógica exige que SÍ exista, 403; si no, podrías crear on-demand o 404.
        raise HTTPException(status_code=403, detail="Therapist not found for user")
    return therapist.id

def get_current_patient_id(
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> UUID:
    stmt = select(PatientModel).where(PatientModel.user_id == user_id)
    patient = session.exec(stmt).first()
    if not patient:
        raise HTTPException(status_code=403, detail="Patient not found for user")
    return patient.id
