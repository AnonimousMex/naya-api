from datetime import datetime, timezone
from typing import Union
from uuid import UUID
from secrets import token_urlsafe

from sqlmodel import Session, select
from fastapi import HTTPException, responses, Request

from app.core.http_response import NayaHttpResponse
from app.core.auth import oauth

from app.constants.response_codes import NayaResponseCodes
from app.constants.user_constants import UserRoles, VerificationModels

from app.models.user_model import UserModel
from app.api.users.user_service import UserService

from app.api.patients.patient_model import PatientModel

from app.api.auth.auth_service import AuthService
from app.api.auth.auth_schema import (
    AdviceResponse,
    VerificationRequest,
    SelectProfileRequest,
)
from app.utils.email import EmailService
from app.utils.security import (
    get_user_token,
    verify_password,
    decode_token,
    get_password_hash,
)

from .auth_model import VerificationCodeModel, VerificationCodePasswordResetModel


class AuthController:
    def __init__(self, session: Session):
        self.session = session

    async def authenticate_external_user(self, request: Request, provider: str):
        try:
            client = getattr(oauth, provider)
            token = await client.authorize_access_token(request)

            if provider == "google":
                user_info = token.get("userinfo")
                email = user_info.get("email")
                name = user_info.get("name")
            else:
                resp = await client.get("user", token=token)
                user_info = resp.json()
                name = user_info.get("name") or user_info.get("login")
                email_resp = await client.get("user/emails", token=token)
                email = next(e["email"] for e in email_resp.json() if e["primary"])

            user = await UserService.get_user_by_email(
                email=email, session=self.session
            )

            if not user:
                user = UserModel(
                    name=name[:20],
                    email=email,
                    password=get_password_hash(token_urlsafe(16)),
                    user_kind=UserRoles.PATIENT,
                    is_verified=True,
                )
                self.session.add(user)
                self.session.commit()
                self.session.refresh(user)

                new_patient = PatientModel(user_id=user.id)
                self.session.add(new_patient)
                self.session.commit()
                self.session.refresh(user)

            if user.user_kind == UserRoles.THERAPIST:
                NayaHttpResponse.forbidden(
                    data={
                        "message": f"Acceso con {provider} no permitido para terapeutas"
                    }
                )

            return await self.login_external(user=user)
        except Exception as e:
            print(f"DEBUG ERROR {provider}: {e}")
            NayaHttpResponse.internal_error()

    async def login_external(self, user: UserModel):
        try:
            if user.user_kind == UserRoles.PATIENT:
                patient_or_therapist_id = user.patient.id if user.patient else user.id
            else:
                patient_or_therapist_id = (
                    user.therapist.id if user.therapist else user.id
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
                    "status": "Login success via External Provider",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user_type": user.user_kind.value,
                }
            )
        except Exception as e:
            print(f"DEBUG ERROR LOGIN: {e}")
            NayaHttpResponse.internal_error()

    async def get_current_user(self, email: str) -> UserModel:
        try:
            user = await UserService.get_user_by_email(
                email=email, session=self.session
            )
            if user is False:
                NayaHttpResponse.not_found(
                    data={"message": NayaResponseCodes.UNEXISTING_USER.detail},
                    error_id=NayaResponseCodes.UNEXISTING_USER.code,
                )
            await self.is_user_verified(user=user)
            return user
        except HTTPException as e:
            raise e
        except Exception:
            NayaHttpResponse.internal_error()

    async def verify_code(self, verification_code_model: Union[VerificationCodeModel]):
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
        except Exception:
            NayaHttpResponse.internal_error()

    async def select_profile_picture(self, request: SelectProfileRequest):
        try:
            relation = AuthService.assign_animal(
                session=self.session,
                user_id=request.user_id,
                id_animal=request.id_animal,
            )
            if not relation:
                NayaHttpResponse.not_found(
                    data={"message": NayaResponseCodes.UNEXISTING_USER.detail},
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
            new_code = await AuthService.generate_unique_verification_code(
                session=self.session,
                model=VerificationModels.VERIFICATION_CODE_PASSWORD_RESET_MODEL,
            )
            user_in_table = await AuthService.user_in_the_verification_codes_tables(
                session=self.session,
                user_id=user.id,
                model=VerificationCodePasswordResetModel,
            )
            if not user_in_table:
                verification_code = (
                    await AuthService.create_verification_code_reset_password(
                        code=new_code, user_id=user.id, session=self.session
                    )
                )
            else:
                verification_code = (
                    await AuthService.update_verification_code_reset_password(
                        code=new_code, user_id=user.id, session=self.session
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
        except Exception:
            NayaHttpResponse.internal_error()

    async def update_user_password(self, user_id: UUID, password: str):
        try:
            await AuthService.update_user_password(
                user_id=user_id, password=password, session=self.session
            )
            return NayaHttpResponse.no_content()
        except HTTPException:
            NayaHttpResponse.internal_error()

    async def resend_code(self, user: UserModel):
        try:
            new_code = await AuthService.generate_unique_verification_code(
                session=self.session, model=VerificationModels.VERIFICATION_CODE_MODEL
            )
            verification_code = await AuthService.update_verification_code(
                code=new_code, user_id=user.id, session=self.session
            )
            await EmailService.send_verification_email(
                to_name=user.name.capitalize(),
                to_email=user.email,
                verification_code=verification_code.code,
            )
            return NayaHttpResponse.no_content()
        except HTTPException:
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
        except Exception:
            NayaHttpResponse.internal_error()

    def verify_user_password(self, user: UserModel, password: str) -> bool:
        if not verify_password(plain_password=password, hashed_password=user.password):
            NayaHttpResponse.unauthorized()
        return True

    async def is_user_verified(self, user: UserModel):
        if not user.is_verified:
            NayaHttpResponse.forbidden(
                data={"message": NayaResponseCodes.UNVERIFIED_USER.detail},
                error_id=NayaResponseCodes.UNVERIFIED_USER.code,
            )

    async def login(self, user: UserModel, password: str):
        return await self.login_external(user=user)

    async def connect_therapist(self, *, token: str, code: str):
        therapist = AuthService.get_therapist_by_code(self.session, code=code)
        decoded = decode_token(token)
        if decoded:
            user_id = decoded.get("sub")
        if not therapist:
            NayaHttpResponse.bad_request(
                data={
                    "message": NayaResponseCodes.UNEXISTING_CODE.detail,
                    "providedValue": {"code": code},
                },
                error_id=NayaResponseCodes.UNEXISTING_CODE.code,
            )
        patient = AuthService.get_patient_by_user_id(self.session, user_id=user_id)
        if not patient:
            NayaHttpResponse.bad_request(
                data={
                    "message": NayaResponseCodes.UNEXISTING_PATIENT.detail,
                    "providedValue": {"patient_id": "unknown"},
                },
                error_id=NayaResponseCodes.UNEXISTING_PATIENT.code,
            )
        if AuthService.connection_exists(
            self.session, therapist_id=therapist.id, patient_id=patient.id
        ):
            NayaHttpResponse.bad_request(
                data={
                    "message": NayaResponseCodes.CONNECTION_EXISTS.detail,
                    "providedValue": {
                        "therapist_id": str(therapist.id),
                        "patient_id": str(patient.id),
                    },
                },
                error_id=NayaResponseCodes.CONNECTION_EXISTS.code,
            )
        AuthService.create_connection(
            self.session, therapist_id=therapist.id, patient_id=patient.id
        )
        patient.is_connected = True
        self.session.add(patient)
        self.session.commit()
        return NayaHttpResponse.no_content()

    async def get_daily_advice(self) -> AdviceResponse:
        advice = AuthService.get_shared_daily_advice(self.session)
        return AdviceResponse(
            id=advice.id, title=advice.title, description=advice.description
        )
