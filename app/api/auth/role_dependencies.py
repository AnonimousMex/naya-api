"""
Dependencies de FastAPI para autorización por rol y autorización por relación
sobre un niño (paciente) específico.

- get_current_user_claims: decodifica el JWT y devuelve un dict con user_id,
  role, patient_id, therapist_id.
- assert_therapist_can_view_child: el terapeuta solo puede ver datos de niños
  con quienes tenga una `connections` activa.
- assert_tutor_can_view_child: el tutor solo puede ver niños vinculados en
  `parent_child`.
- assert_can_view_child: combina ambas según el rol del caller. Niños patients
  reciben 403 explícito en endpoints clínicos.
"""
from uuid import UUID
from typing import Dict, Any

import jwt
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.auth.auth_dependencies import oauth2_scheme
from app.api.auth.auth_model import ConnectionModel
from app.api.parents.parent_model import ParentChildModel
from app.constants.user_constants import UserRoles
from app.core.database import SessionDep
from app.core.settings import settings


def get_current_user_claims(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user = payload.get("user", {})
        if not user.get("user_id") and not payload.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user",
            )
        return {
            "user_id": user.get("user_id") or payload.get("sub"),
            "role": user.get("role") or user.get("user_type"),
            "patient_id": user.get("patient_id"),
            "therapist_id": user.get("therapist_id"),
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def _therapist_has_connection(
    session: Session, *, therapist_id: UUID, patient_id: UUID
) -> bool:
    stmt = select(ConnectionModel).where(
        ConnectionModel.therapist_id == therapist_id,
        ConnectionModel.patient_id == patient_id,
    )
    return session.exec(stmt).first() is not None


def _tutor_has_child(
    session: Session, *, parent_user_id: UUID, patient_id: UUID
) -> bool:
    stmt = select(ParentChildModel).where(
        ParentChildModel.parent_user_id == parent_user_id,
        ParentChildModel.patient_id == patient_id,
    )
    return session.exec(stmt).first() is not None


def assert_therapist_can_view_child(
    child_id: UUID,
    session: SessionDep,
    claims: Dict[str, Any] = Depends(get_current_user_claims),
) -> Dict[str, Any]:
    role = (claims.get("role") or "").upper()
    if role != UserRoles.THERAPIST.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only therapists can access this resource",
        )
    therapist_id = claims.get("therapist_id")
    if not therapist_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has no therapist_id",
        )
    if not _therapist_has_connection(
        session, therapist_id=UUID(therapist_id), patient_id=child_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Therapist not connected to this child",
        )
    return claims


def assert_tutor_can_view_child(
    child_id: UUID,
    session: SessionDep,
    claims: Dict[str, Any] = Depends(get_current_user_claims),
) -> Dict[str, Any]:
    role = (claims.get("role") or "").upper()
    if role != UserRoles.PARENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tutors can access this resource",
        )
    user_id = claims.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has no user_id",
        )
    if not _tutor_has_child(
        session, parent_user_id=UUID(user_id), patient_id=child_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tutor not linked to this child",
        )
    return claims


def assert_current_parent(
    claims: Dict[str, Any] = Depends(get_current_user_claims),
) -> Dict[str, Any]:
    """Sólo permite acceder al endpoint si el rol del token es PARENT."""
    role = (claims.get("role") or "").upper()
    if role != UserRoles.PARENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tutors (PARENT) can access this resource",
        )
    if not claims.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has no user_id",
        )
    return claims


def assert_can_view_child_history(
    child_id: UUID,
    session: SessionDep,
    claims: Dict[str, Any] = Depends(get_current_user_claims),
) -> Dict[str, Any]:
    """Permite acceso a terapeuta vinculado o tutor vinculado. Niño NO puede."""
    role = (claims.get("role") or "").upper()
    if role == UserRoles.THERAPIST.value:
        therapist_id = claims.get("therapist_id")
        if therapist_id and _therapist_has_connection(
            session, therapist_id=UUID(therapist_id), patient_id=child_id
        ):
            return claims
    elif role == UserRoles.PARENT.value:
        user_id = claims.get("user_id")
        if user_id and _tutor_has_child(
            session, parent_user_id=UUID(user_id), patient_id=child_id
        ):
            return claims
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to view this child's history",
    )
