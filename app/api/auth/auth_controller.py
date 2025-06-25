from typing import Union
from uuid import UUID

from sqlmodel import Session, select
from fastapi import HTTPException

from app.api.patients.patient_model import PatientModel
from app.api.pictures.picture_animal_emotion_model import PictureAnimalEmotionModel
from app.core.http_response import NayaHttpResponse

from app.constants.response_codes import NayaResponseCodes
from app.constants.user_constants import VerificationModels

from app.api.users.user_model import UserModel
from app.api.users.user_service import UserService


from app.api.auth.auth_service import AuthService
from app.api.auth.auth_schema import VerificationRequest, SelectProfileRequest

from .auth_model import VerificationCodeModel


class AuthController:
    def __init__(self, session: Session):
        self.session = session

    async def get_current_user(self, email: str) -> UserModel:
        try:
            user = await UserService.get_user_by_email(
                email=email, session=self.session
            )

            if user is False:
                NayaHttpResponse.not_found(
                    data={
                        "message": NayaResponseCodes.UNEXISTING_USER.detail,
                    },
                    error_id=NayaResponseCodes.UNEXISTING_USER.code,
                )

            await self.is_user_verified(user=user)

            return user

        except HTTPException as e:
            raise e

        except Exception as e:
            NayaHttpResponse.internal_error()

    async def verify_code(
        self,
        verification_code_model: Union[VerificationCodeModel],
    ):
        try:
            if isinstance(verification_code_model, VerificationCodeModel):
                user_id = verification_code_model.user_id

                await AuthService.update_verification_code_status(
                    verification_code=verification_code_model, session=self.session
                )

                await UserService.verify_user(user_id=user_id, session=self.session)
            else:
                await AuthService.update_verification_code_status(
                    verification_code=verification_code_model, session=self.session
                )

            return NayaHttpResponse.no_content()

        except HTTPException as e:
            raise e

        except Exception as e:
            NayaHttpResponse.internal_error()

    async def select_profile_picture(self, request: SelectProfileRequest):
        try:
            relation = AuthService.assign_animal_and_picture(
                session=self.session,
                user_id=request.user_id,
                id_picture=request.id_picture,
                id_animal=request.id_animal,
                id_emotion=request.id_emotion,
            )

            if not relation:
                NayaHttpResponse.not_found(
                    data={
                        "message": NayaResponseCodes.UNEXISTING_USER.detail,
                    },
                    error_id=NayaResponseCodes.UNEXISTING_USER.code,
                )

            return NayaHttpResponse.no_content()

        except Exception:
            NayaHttpResponse.internal_error()

    async def get_verification_code_by_code(
        self, request: VerificationRequest, model=VerificationModels
    ):
        verification_code = await AuthService.get_verification_code(
            code=request.code, table=model, session=self.session
        )

        if not verification_code:
            NayaHttpResponse.bad_request(
                data={
                    "message": NayaResponseCodes.UNEXISTING_CODE.detail,
                    "providedValue": {"code": request.code},
                },
                error_id=NayaResponseCodes.UNEXISTING_CODE.code,
            )

        return verification_code

    def verify_is_code_alive(self, verification_code: VerificationCodeModel) -> bool:
        if not verification_code.is_alive:
            NayaHttpResponse.bad_request(
                data={
                    "message": NayaResponseCodes.ALREADY_USED_CODE.detail,
                    "providedValue": {"code": verification_code.code},
                },
                error_id=NayaResponseCodes.ALREADY_USED_CODE.code,
            )

        return True
