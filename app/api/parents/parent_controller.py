from typing import List
from sqlmodel import Session, select
from app.api.therapists.therapist_model import TherapistModel
from app.api.professional_experience.professional_experience_model import ProfessionalExperienceModel
from app.api.specialties.specialty_model import SpecialtyModel, SpecialtyTherapistModel
from app.models.user_model import UserModel
from app.api.parents.parent_schema import TherapistSchema, SpecialtySchema

class ParentController:
    def __init__(self, session: Session):
        self.session = session

    async def list_therapists(self) -> List[TherapistSchema]:
        statement = select(
            TherapistModel, 
            UserModel
        ).join(
            UserModel, 
            TherapistModel.user_id == UserModel.id
        )
        
        results = self.session.exec(statement).all()
        
        therapists = []
        for therapist, user in results:
            exp_statement = select(ProfessionalExperienceModel).where(
                ProfessionalExperienceModel.id_therapist == therapist.id
            )
            experiences = self.session.exec(exp_statement).all()
            
            specialty_statement = select(
                SpecialtyModel
            ).join(
                SpecialtyTherapistModel,
                SpecialtyModel.id == SpecialtyTherapistModel.id_specialty
            ).where(
                SpecialtyTherapistModel.id_therapist == therapist.id
            )
            specialties = self.session.exec(specialty_statement).all()
            formatted_experiences = [
                {
                    "title": exp.institute,
                    "years": exp.period,
                    "description": exp.activity or f"{exp.position} en {exp.institute}"
                }
                for exp in experiences
            ]
            
            formatted_specialties = [
                SpecialtySchema(
                    name=spec.name,
                    description=None  
                )
                for spec in specialties
            ]
            
            address_parts = [
                therapist.street,
                therapist.city,
                therapist.state,
                therapist.postal_code
            ]
            full_address = ", ".join([part for part in address_parts if part])
            
            therapist_data = TherapistSchema(
                therapist_id=str(therapist.id),
                name=user.name,
                description=therapist.description or "Hola, soy {user.name}, terapeuta en nuestra app.",
                phone=therapist.phone or "No hay teléfono registrado",
                email=user.email or "No hay email registrado",
                address=full_address or "No hay dirección registrada",
                specialties=formatted_specialties,
                experiences=formatted_experiences
            )
            
            therapists.append(therapist_data)
        
        return therapists
