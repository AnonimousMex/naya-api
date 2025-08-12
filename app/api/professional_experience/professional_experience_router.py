from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.database import SessionDep
from ..auth.auth_dependencies import get_current_therapist_id
from app.api.professional_experience.professional_experience_service import ProfessionalExperienceService
from app.api.professional_experience.professional_experience_schema import (
    ProfessionalExperienceCreate,
    ProfessionalExperienceUpdate,
    ProfessionalExperienceResponse
)
from app.core.http_response import NayaHttpResponse, NayaResponseModel

professional_experience_router = APIRouter()


@professional_experience_router.post(
    "/professional-experience", 
    response_model=NayaResponseModel[ProfessionalExperienceResponse]
)
async def create_professional_experience(
    experience_data: ProfessionalExperienceCreate,
    session: SessionDep,
    current_therapist_id: UUID = Depends(get_current_therapist_id)
):
    """Crear una experiencia profesional para el terapeuta autenticado."""
    # Verificar que el terapeuta solo puede crear experiencias para sí mismo
    if experience_data.id_therapist != current_therapist_id:
        return NayaHttpResponse.forbidden(
            data={"message": "Solo puedes crear experiencias para tu propio perfil"},
            error_id="FORBIDDEN_EXPERIENCE_CREATION"
        )
    
    experience = await ProfessionalExperienceService.create_experience(experience_data, session)
    return NayaHttpResponse.created(data=experience)


@professional_experience_router.get(
    "/professional-experience", 
    response_model=NayaResponseModel[List[ProfessionalExperienceResponse]]
)
async def get_therapist_experiences(
    session: SessionDep,
    current_therapist_id: UUID = Depends(get_current_therapist_id)
):
    """Obtener experiencias profesionales del terapeuta autenticado."""
    experiences = await ProfessionalExperienceService.get_therapist_experiences(
        current_therapist_id, session
    )
    return NayaHttpResponse.ok(data=experiences)


@professional_experience_router.get(
    "/therapist/{therapist_id}/professional-experience", 
    response_model=NayaResponseModel[List[ProfessionalExperienceResponse]]
)
async def get_therapist_experiences_by_id(
    therapist_id: UUID,
    session: SessionDep
):
    """Obtener experiencias profesionales de un terapeuta específico."""
    experiences = await ProfessionalExperienceService.get_therapist_experiences(
        therapist_id, session
    )
    return NayaHttpResponse.ok(data=experiences)


@professional_experience_router.put(
    "/professional-experience/{experience_id}", 
    response_model=NayaResponseModel[ProfessionalExperienceResponse]
)
async def update_professional_experience(
    experience_id: UUID,
    update_data: ProfessionalExperienceUpdate,
    session: SessionDep,
    current_therapist_id: UUID = Depends(get_current_therapist_id)
):
    """Actualizar una experiencia profesional."""
    # Verificar que la experiencia pertenece al terapeuta autenticado
    experience = await ProfessionalExperienceService.get_experience_by_id(experience_id, session)
    if not experience:
        return NayaHttpResponse.not_found(
            data={"message": "Experiencia no encontrada"},
            error_id="EXPERIENCE_NOT_FOUND"
        )
    
    if experience.id_therapist != current_therapist_id:
        return NayaHttpResponse.forbidden(
            data={"message": "No tienes permisos para editar esta experiencia"},
            error_id="FORBIDDEN_EXPERIENCE_UPDATE"
        )
    
    updated_experience = await ProfessionalExperienceService.update_experience(
        experience_id, update_data, session
    )
    
    return NayaHttpResponse.ok(data=updated_experience)


@professional_experience_router.delete("/professional-experience/{experience_id}")
async def delete_professional_experience(
    experience_id: UUID,
    session: SessionDep,
    current_therapist_id: UUID = Depends(get_current_therapist_id)
):
    """Eliminar una experiencia profesional."""
    # Verificar que la experiencia pertenece al terapeuta autenticado
    experience = await ProfessionalExperienceService.get_experience_by_id(experience_id, session)
    if not experience:
        return NayaHttpResponse.not_found(
            data={"message": "Experiencia no encontrada"},
            error_id="EXPERIENCE_NOT_FOUND"
        )
    
    if experience.id_therapist != current_therapist_id:
        return NayaHttpResponse.forbidden(
            data={"message": "No tienes permisos para eliminar esta experiencia"},
            error_id="FORBIDDEN_EXPERIENCE_DELETE"
        )
    
    deleted = await ProfessionalExperienceService.delete_experience(experience_id, session)
    
    if deleted:
        return NayaHttpResponse.ok(
            data={"message": "Experiencia eliminada correctamente"}
        )
    else:
        return NayaHttpResponse.internal_error()
