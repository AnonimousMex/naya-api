from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from app.api.professional_experience.professional_experience_model import ProfessionalExperienceModel
from app.api.professional_experience.professional_experience_schema import (
    ProfessionalExperienceCreate,
    ProfessionalExperienceUpdate
)
from app.core.http_response import NayaHttpResponse


class ProfessionalExperienceService:
    
    @staticmethod
    async def create_experience(
        experience_data: ProfessionalExperienceCreate, 
        session: Session
    ) -> ProfessionalExperienceModel:
        """Crear una nueva experiencia profesional."""
        try:
            experience = ProfessionalExperienceModel(**experience_data.model_dump())
            session.add(experience)
            session.commit()
            session.refresh(experience)
            return experience
        except Exception:
            session.rollback()
            NayaHttpResponse.internal_error()
    
    @staticmethod
    async def get_therapist_experiences(
        therapist_id: UUID, 
        session: Session
    ) -> List[ProfessionalExperienceModel]:
        """Obtener experiencias profesionales de un terapeuta."""
        try:
            statement = select(ProfessionalExperienceModel).where(
                ProfessionalExperienceModel.id_therapist == therapist_id
            )
            experiences = session.exec(statement).all()
            return experiences
        except Exception:
            NayaHttpResponse.internal_error()
    
    @staticmethod
    async def update_experience(
        experience_id: UUID,
        update_data: ProfessionalExperienceUpdate,
        session: Session
    ) -> Optional[ProfessionalExperienceModel]:
        """Actualizar una experiencia profesional."""
        try:
            experience = session.get(ProfessionalExperienceModel, experience_id)
            if not experience:
                return None
            
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(experience, field, value)
            
            session.add(experience)
            session.commit()
            session.refresh(experience)
            return experience
            
        except Exception:
            session.rollback()
            NayaHttpResponse.internal_error()
    
    @staticmethod
    async def delete_experience(experience_id: UUID, session: Session) -> bool:
        """Eliminar una experiencia profesional."""
        try:
            experience = session.get(ProfessionalExperienceModel, experience_id)
            if not experience:
                return False
            
            session.delete(experience)
            session.commit()
            return True
            
        except Exception:
            session.rollback()
            NayaHttpResponse.internal_error()
    
    @staticmethod
    async def get_experience_by_id(
        experience_id: UUID, 
        session: Session
    ) -> Optional[ProfessionalExperienceModel]:
        """Obtener una experiencia específica por ID."""
        try:
            experience = session.get(ProfessionalExperienceModel, experience_id)
            return experience
        except Exception:
            NayaHttpResponse.internal_error()
