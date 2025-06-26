from typing import Union
from uuid import UUID

from sqlmodel import Session, select
from fastapi import HTTPException, responses

from app.core.http_response import NayaHttpResponse

from app.constants.response_codes import NayaResponseCodes
from app.constants.user_constants import UserRoles, VerificationModels

from app.api.users.user_model import UserModel
from app.api.users.user_service import UserService


from app.api.Auth.auth_service import AuthService
from app.api.Auth.auth_schema import VerificationRequest, SelectProfileRequest
from app.utils.email import EmailService
from app.utils.security import get_user_token, verify_password

from .auth_model import VerificationCodeModel, VerificationCodePasswordResetModel


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

    async def request_password_reset_verification_code(self, user: UserModel):
            try:
                new_verification_code = await AuthService.generate_unique_verification_code(
                    session=self.session,
                    model=VerificationModels.VERIFICATION_CODE_PASSWORD_RESET_MODEL,
                )

                user_in_the_verification_code_password_reset_table = (
                    await AuthService.user_in_the_verification_codes_tables(
                        session=self.session, user_id=user.id, model=VerificationCodePasswordResetModel
                    )
                )
                if (
                    not user_in_the_verification_code_password_reset_table
                ):
                    verification_code = (
                        await AuthService.create_verification_code_reset_password(
                            code=new_verification_code,
                            user_id=user.id,
                            session=self.session,
                        )
                    )
                else:
                    verification_code = (
                        await AuthService.update_verification_code_reset_password(
                            code=new_verification_code,
                            user_id=user.id,
                            session=self.session,
                        )
                    )

                await EmailService.send_verification_email(
                    to_name=user.name.capitalize(),
                    to_email=user.email,
                    verification_code=verification_code.code,
                )

                return NayaHttpResponse.no_content()

            except HTTPException as e:
                raise e

            except Exception as e:
                NayaHttpResponse.internal_error()

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

    async def get_current_user_from_login(self, email: str) -> UserModel:
        try:
            user = await UserService.get_user_by_email(
                email=email, session=self.session
            )

            if user is False:
                NayaHttpResponse.unauthorized()

            return user
        except HTTPException as e:
            raise e

        except Exception as e:
            NayaHttpResponse.internal_error()

    def verify_user_password(self, user: UserModel, password: str) -> bool:
        is_valid_password = verify_password(
            plain_password=password, hashed_password=user.password
        )

        if not is_valid_password:
            NayaHttpResponse.unauthorized()

        return True

    async def is_user_verified(self, user: UserModel):
        if not user.is_verified:
            NayaHttpResponse.forbidden(
                data={
                    "message": NayaResponseCodes.UNVERIFIED_USER.detail,
                },
                error_id=NayaResponseCodes.UNVERIFIED_USER.code,
            )

    async def login(self, user: UserModel, password: str):
        try:
            patient_or_therapist_id = (
                user.patient.id
                if user.user_kind == UserRoles.PATIENT
                else user.therapist.id
            )

            access_token = get_user_token(
                user=user,
                user_type=user.user_kind.value,
                is_refresh=False,
                patient_or_therapist_id=patient_or_therapist_id,
            )

            refresh_token = get_user_token(
                user=user,
                user_type=user.user_kind.value,
                is_refresh=True,
                patient_or_therapist_id=patient_or_therapist_id,
            )

            return responses.JSONResponse(
                content={
                    "status": "Login success",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            )
        except HTTPException as e:
            raise e

        except Exception as e:
            NayaHttpResponse.internal_error()
