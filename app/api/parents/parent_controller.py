from typing import List
from uuid import UUID

from sqlmodel import Session, select

from app.api.animals.animal_model import AnimalModel
from app.api.parents.parent_model import ParentChildModel
from app.api.parents.parent_schema import (
    AnimalSchema,
    ChildSchema,
    SpecialtySchema,
    TherapistSchema,
)
from app.api.patients.patient_model import PatientModel
from app.api.professional_experience.professional_experience_model import ProfessionalExperienceModel
from app.api.specialties.specialty_model import SpecialtyModel, SpecialtyTherapistModel
from app.api.therapists.therapist_model import TherapistModel
from app.models.user_model import UserModel


class ParentController:
    def __init__(self, session: Session):
        self.session = session

    def list_children(self, parent_user_id: UUID) -> List[ChildSchema]:
        """
        Devuelve los niños vinculados al tutor logueado, con los datos
        mínimos para que el frontend pueda mostrar un selector.
        """
        stmt = (
            select(PatientModel, UserModel, AnimalModel)
            .join(UserModel, UserModel.id == PatientModel.user_id)
            .join(
                ParentChildModel,
                ParentChildModel.patient_id == PatientModel.id,
            )
            .join(AnimalModel, AnimalModel.id == PatientModel.animal_id, isouter=True)
            .where(ParentChildModel.parent_user_id == parent_user_id)
        )
        rows = self.session.exec(stmt).all()
        children: List[ChildSchema] = []
        for patient, user, animal in rows:
            children.append(
                ChildSchema(
                    patient_id=str(patient.id),
                    name=user.name,
                    email=user.email,
                    animal=AnimalSchema(
                        name=animal.name,
                        color_ui=animal.color_ui,
                        animal_key=animal.animal_key,
                    )
                    if animal is not None
                    else None,
                )
            )
        return children

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
