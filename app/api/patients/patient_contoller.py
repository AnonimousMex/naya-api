from fastapi import HTTPException
from sqlmodel import Session

from app.api.auth.auth_service import AuthService
from app.api.patients.patient_schema import PatientCreateSchema, PatientResponseSchema
from app.api.patients.patient_services import PatientService
from app.api.users.user_controller import UserController
from app.api.users.user_schema import UserCreateSchema, UserResponseSchema
from app.api.users.user_service import UserService
from app.constants.user_constants import UserRoles, VerificationModels
from app.core.http_response import NayaHttpResponse
from app.utils.email import EmailService


class PatientController:
    def __init__(self, session: Session):
        self.session = session

    async def create_patient(
        self, patient_data: PatientCreateSchema
    ) -> PatientResponseSchema:
        try:

            user_controller = UserController(session=self.session)

            await user_controller.validate_exixting_user(user_email=patient_data.email)

            user_data: UserCreateSchema = patient_data

            user = await UserService.create_user(
                user_data=user_data, user_kind=UserRoles.PATIENT, session=self.session
            )

            patient = await PatientService.create_patient(
                user=user, session=self.session
            )

            new_verification_code = await AuthService.generate_unique_verification_code(
                session=self.session, model=VerificationModels.VERIFICATION_CODE_MODEL
            )

            verification_code = await AuthService.create_verification_code(
                code=new_verification_code, user_id=user.id, session=self.session
            )

            await EmailService.send_verification_email(
                to_name=user.name.capitalize(),
                to_email=user.email,
                verification_code=verification_code.code,
            )

            user_dump = UserResponseSchema.model_validate(user).model_dump()

            response = PatientResponseSchema(**user_dump, patient_id=patient.id)

            return response

        except HTTPException as e:
            raise e

        except Exception as e:
            NayaHttpResponse.internal_error(e)