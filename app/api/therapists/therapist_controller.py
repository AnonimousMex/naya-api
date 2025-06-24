from uuid import UUID

from fastapi import HTTPException

from sqlmodel import Session

from app.api.Auth.auth_service import AuthService
from app.api.therapists.therapist_services import TherapistService
from app.constants.response_codes import NayaResponseCodes
from app.core.http_response import NayaHttpResponse

from app.constants.user_constants import UserRoles

from app.api.users.user_service import UserService
from app.api.users.user_controller import UserController
from app.api.users.user_schema import UserCreateSchema, UserResponseSchema


from .therapist_schema import TherapistResponseSchema, TherapistCreateSchema


class TherapistController:
    def __init__(self, session: Session):
        self.session = session

    async def create_therapist(
        self, therapist_data: TherapistCreateSchema
    ) -> TherapistResponseSchema:
        try:
            user_controller = UserController(session=self.session)

            await user_controller.validate_exixting_user(
                user_email=therapist_data.email
            )

            # We should do a stronger validation if schemas change (UserCreateSchema and PatientCreateSchema)
            user_data: UserCreateSchema = therapist_data

            user = await UserService.create_user(
                user_data=user_data, user_kind=UserRoles.THERAPIST, session=self.session
            )

            therapist = await TherapistService.create_therapist(
                user=user, session=self.session
            )

            # new_verification_code = await AuthService.generate_unique_verification_code(
            #     session=self.session, model=VerificationModels.VERIFICATION_CODE_MODEL
            # )

            # verification_code = await AuthService.create_verification_code(
            #     code=new_verification_code, user_id=user.id, session=self.session
            # )

            # await EmailService.send_verification_email(
            #     to_name=user.name.capitalize(),
            #     to_email=user.email,
            #     verification_code=verification_code.code,
            # )

            user_dump = UserResponseSchema.model_validate(user).model_dump()

            response = TherapistResponseSchema(**user_dump, therapist_id=therapist.id)

            return response

        except HTTPException as e:
            raise e

        except Exception as e:
            NayaHttpResponse.internal_error()

    async def get_therapist_by_id(self, therapist_id: UUID) -> TherapistResponseSchema:
        try:
            therapist = await TherapistService.get_therapist_by_id(
                therapist_id=therapist_id, session=self.session
            )

            if therapist is None:
                NayaHttpResponse.not_found(
                    data={
                        "message": NayaResponseCodes.UNEXISTING_THERAPIST.detail,
                        "providedValue": str(therapist_id),
                    },
                    error_id=NayaResponseCodes.UNEXISTING_THERAPIST.code,
                )

            user_dump = UserResponseSchema.model_validate(therapist.user).model_dump()

            response = TherapistResponseSchema(**user_dump, therapist_id=therapist_id)

            return response

        except HTTPException as e:
            raise e

        except Exception as e:
            NayaHttpResponse.internal_error()
