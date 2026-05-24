from sqlmodel import Session
from app.api.patients.patient_model import PatientModel
from app.models.user_model import UserModel
from app.core.http_response import NayaHttpResponse


class PatientService:
    # Consider receiving an object of type PatientCreateSchema in case extra fields on that schema are added
    @staticmethod
    async def create_patient(user: UserModel, session: Session) -> PatientModel:
        try:
            # Consider doing dump
            new_patient = PatientModel(user=user, user_id=user.id)

            session.add(new_patient)
            session.commit()
            session.refresh(new_patient)

            return new_patient
        except Exception as e:
            import traceback
            with open("error.log", "a") as f:
                traceback.print_exc(file=f)
            NayaHttpResponse.internal_error()