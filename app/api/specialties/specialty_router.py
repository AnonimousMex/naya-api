from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.database import SessionDep
from app.api.auth.auth_dependencies import get_current_therapist_id
from app.api.specialties.specialty_service import SpecialtyService
from app.api.specialties.specialty_schema import (
    SpecialtyCreate,
    SpecialtyResponse,
    TherapistSpecialtyAssign
)
from app.core.http_response import NayaHttpResponse, NayaResponseModel

specialty_router = APIRouter()


@specialty_router.post("/specialties", response_model=NayaResponseModel[SpecialtyResponse])
async def create_specialty(
    specialty_data: SpecialtyCreate,
    session: SessionDep
):
    """Crear una nueva especialidad."""
    specialty = await SpecialtyService.create_specialty(specialty_data, session)
    return NayaHttpResponse.created(data=specialty)


@specialty_router.get("/specialties", response_model=NayaResponseModel[List[SpecialtyResponse]])
async def get_all_specialties(session: SessionDep):
    """Obtener todas las especialidades."""
    specialties = await SpecialtyService.get_all_specialties(session)
    return NayaHttpResponse.ok(data=specialties)


@specialty_router.post("/therapist/specialties")
async def assign_specialties_to_therapist(
    assignment_data: TherapistSpecialtyAssign,
    session: SessionDep,
    current_therapist_id: UUID = Depends(get_current_therapist_id)
):
    """Asignar especialidades al terapeuta autenticado."""
    # Verificar que el terapeuta solo puede asignar especialidades a sí mismo
    if assignment_data.therapist_id != current_therapist_id:
        return NayaHttpResponse.forbidden(
            data={"message": "Solo puedes asignar especialidades a tu propio perfil"},
            error_id="FORBIDDEN_SPECIALTY_ASSIGNMENT"
        )
    
    success = await SpecialtyService.assign_specialties_to_therapist(assignment_data, session)
    if success:
        return NayaHttpResponse.ok(
            data={"message": "Especialidades asignadas correctamente"}
        )
    else:
        return NayaHttpResponse.internal_error()


@specialty_router.get("/therapist/specialties", response_model=NayaResponseModel[List[SpecialtyResponse]])
async def get_therapist_specialties(
    session: SessionDep,
    current_therapist_id: UUID = Depends(get_current_therapist_id)
):
    """Obtener especialidades del terapeuta autenticado."""
    specialties = await SpecialtyService.get_therapist_specialties(current_therapist_id, session)
    return NayaHttpResponse.ok(data=specialties)


@specialty_router.get("/therapist/{therapist_id}/specialties", response_model=NayaResponseModel[List[SpecialtyResponse]])
async def get_therapist_specialties_by_id(
    therapist_id: UUID,
    session: SessionDep
):
    """Obtener especialidades de un terapeuta específico."""
    specialties = await SpecialtyService.get_therapist_specialties(therapist_id, session)
    return NayaHttpResponse.ok(data=specialties)
