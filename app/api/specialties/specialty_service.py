from typing import List
from uuid import UUID
from sqlmodel import Session, select
from app.api.specialties.specialty_model import SpecialtyModel, SpecialtyTherapistModel
from app.api.specialties.specialty_schema import SpecialtyCreate, TherapistSpecialtyAssign
from app.api.therapists.therapist_model import TherapistModel
from app.core.http_response import NayaHttpResponse


class SpecialtyService:
    
    @staticmethod
    async def create_specialty(specialty_data: SpecialtyCreate, session: Session) -> SpecialtyModel:
        """Crear una nueva especialidad."""
        try:
            specialty = SpecialtyModel(**specialty_data.model_dump())
            session.add(specialty)
            session.commit()
            session.refresh(specialty)
            return specialty
        except Exception:
            session.rollback()
            NayaHttpResponse.internal_error()
    
    @staticmethod
    async def get_all_specialties(session: Session) -> List[SpecialtyModel]:
        """Obtener todas las especialidades."""
        try:
            statement = select(SpecialtyModel)
            specialties = session.exec(statement).all()
            return specialties
        except Exception:
            NayaHttpResponse.internal_error()
    
    @staticmethod
    async def assign_specialties_to_therapist(
        assignment_data: TherapistSpecialtyAssign, 
        session: Session
    ) -> bool:
        """Asignar especialidades a un terapeuta."""
        try:
            # Verificar que el terapeuta existe
            therapist = session.get(TherapistModel, assignment_data.therapist_id)
            if not therapist:
                NayaHttpResponse.not_found(
                    data={"message": "Therapist not found"},
                    error_id="THERAPIST_NOT_FOUND"
                )
            
            # Eliminar asignaciones previas
            prev_assignments = session.exec(
                select(SpecialtyTherapistModel)
                .where(SpecialtyTherapistModel.id_therapist == assignment_data.therapist_id)
            ).all()
            
            for assignment in prev_assignments:
                session.delete(assignment)
            
            # Crear nuevas asignaciones
            for specialty_id in assignment_data.specialty_ids:
                # Verificar que la especialidad existe
                specialty = session.get(SpecialtyModel, specialty_id)
                if not specialty:
                    continue
                
                new_assignment = SpecialtyTherapistModel(
                    id_therapist=assignment_data.therapist_id,
                    id_specialty=specialty_id
                )
                session.add(new_assignment)
            
            session.commit()
            return True
            
        except Exception:
            session.rollback()
            NayaHttpResponse.internal_error()
    
    @staticmethod
    async def get_therapist_specialties(therapist_id: UUID, session: Session) -> List[SpecialtyModel]:
        """Obtener especialidades de un terapeuta."""
        try:
            statement = (
                select(SpecialtyModel)
                .join(SpecialtyTherapistModel)
                .where(SpecialtyTherapistModel.id_therapist == therapist_id)
            )
            specialties = session.exec(statement).all()
            return specialties
        except Exception:
            NayaHttpResponse.internal_error()
