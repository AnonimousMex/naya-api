from datetime import datetime, timedelta, timezone
from typing import Union
from uuid import UUID
from app.core.logger import logger
from app.core import metrics
from app.core import sentry_events as sentry

from sqlmodel import Session, select
from fastapi import HTTPException, responses

from app.core.http_response import NayaHttpResponse

from app.constants.response_codes import NayaResponseCodes
from app.constants.user_constants import UserRoles, VerificationModels

from app.models.user_model import UserModel
from app.api.users.user_service import UserService


from app.api.auth.auth_service import AuthService
from app.api.auth.auth_schema import (
    AdviceResponse,
    VerificationRequest,
    SelectProfileRequest,
)
from app.utils.email import EmailService
from app.utils.security import get_user_token, verify_password, decode_token, get_user_id_from_token

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
                logger.warning(
                    "auth.user_not_found",
                    extra={
                        "event": "auth.user_not_found",
                        "email_domain": email.split("@", 1)[1] if "@" in email else "<no-domain>",
                    },
                )
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
            metrics.MODULE_ERRORS.labels(module="auth").inc()
            logger.exception(
                "auth.get_current_user_failed",
                extra={
                    "event": "auth.get_current_user_failed",
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
            )
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
                logger.info(
                    "auth.user_verified",
                    extra={
                        "event": "auth.user_verified",
                        "user_id": str(user_id),
                        "kind": "signup",
                    },
                )
            else:
                await AuthService.update_verification_code_status(
                    verification_code=verification_code_model, session=self.session
                )
                logger.info(
                    "auth.verification_code_consumed",
                    extra={
                        "event": "auth.verification_code_consumed",
                        "kind": "password_reset",
                    },
                )

            return NayaHttpResponse.no_content()

        except HTTPException as e:
            raise e

        except Exception as e:
            metrics.MODULE_ERRORS.labels(module="auth").inc()
            logger.exception(
                "auth.verify_code_failed",
                extra={
                    "event": "auth.verify_code_failed",
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
            )
            NayaHttpResponse.internal_error()

    async def select_profile_picture(self, request: SelectProfileRequest):
        try:
            relation = AuthService.assign_animal(
                session=self.session,
                user_id=request.user_id,
                id_animal=request.id_animal,
            )

            if not relation:
                logger.warning(
                    "auth.select_profile_user_not_found",
                    extra={
                        "event": "auth.select_profile_user_not_found",
                        "user_id": str(request.user_id),
                        "animal_id": str(request.id_animal),
                    },
                )
                NayaHttpResponse.not_found(
                    data={
                        "message": NayaResponseCodes.UNEXISTING_USER.detail,
                    },
                    error_id=NayaResponseCodes.UNEXISTING_USER.code,
                )

            logger.info(
                "auth.profile_picture_selected",
                extra={
                    "event": "auth.profile_picture_selected",
                    "user_id": str(request.user_id),
                    "animal_id": str(request.id_animal),
                },
            )
            return NayaHttpResponse.no_content()

        except HTTPException:
            raise
        except Exception as e:
            metrics.MODULE_ERRORS.labels(module="auth").inc()
            logger.exception(
                "auth.select_profile_failed",
                extra={
                    "event": "auth.select_profile_failed",
                    "user_id": str(request.user_id),
                    "animal_id": str(request.id_animal),
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
            )
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
            new_password_reset_code = (
                await AuthService.generate_unique_verification_code(
                    session=self.session,
                    model=VerificationModels.VERIFICATION_CODE_PASSWORD_RESET_MODEL,
                )
            )

            user_in_the_verification_code_password_reset_table = (
                await AuthService.user_in_the_verification_codes_tables(
                    session=self.session,
                    user_id=user.id,
                    model=VerificationCodePasswordResetModel,
                )
            )
            if not user_in_the_verification_code_password_reset_table:
                verification_code = (
                    await AuthService.create_verification_code_reset_password(
                        code=new_password_reset_code,
                        user_id=user.id,
                        session=self.session,
                    )
                )
            else:
                verification_code = (
                    await AuthService.update_verification_code_reset_password(
                        code=new_password_reset_code,
                        user_id=user.id,
                        session=self.session,
                    )
                )

            await EmailService.send_verification_email(
                to_name=user.name.capitalize(),
                to_email=user.email,
                verification_code=verification_code.code,
            )

            metrics.VERIFICATION_CODES_GENERATED.labels(kind="password_reset").inc()
            logger.info(
                "auth.verification_code_generated",
                extra={
                    "event": "auth.verification_code_generated",
                    "kind": "password_reset",
                    "user_id": str(user.id),
                },
            )

            return NayaHttpResponse.no_content()

        except HTTPException as e:
            raise e

        except Exception as e:
            metrics.MODULE_ERRORS.labels(module="auth").inc()
            NayaHttpResponse.internal_error()

    async def update_user_password(self, user_id: UUID, password: str):
        try:
            await AuthService.update_user_password(
                user_id=user_id, password=password, session=self.session
            )

            logger.info(
                "auth.password_updated",
                extra={"event": "auth.password_updated", "user_id": str(user_id)},
            )
            return NayaHttpResponse.no_content()
        except HTTPException as e:
            metrics.MODULE_ERRORS.labels(module="auth").inc()
            logger.exception(
                "auth.password_update_failed",
                extra={
                    "event": "auth.password_update_failed",
                    "user_id": str(user_id),
                    "detail": str(e.detail),
                },
            )
            NayaHttpResponse.internal_error()

    async def resend_code(self, user: UserModel):
        try:
            new_verification_code = await AuthService.generate_unique_verification_code(
                session=self.session,
                model=VerificationModels.VERIFICATION_CODE_MODEL,
            )

            verification_code = await AuthService.update_verification_code(
                code=new_verification_code,
                user_id=user.id,
                session=self.session,
            )

            await EmailService.send_verification_email(
                to_name=user.name.capitalize(),
                to_email=user.email,
                verification_code=verification_code.code,
            )

            metrics.VERIFICATION_CODES_GENERATED.labels(kind="signup_resend").inc()
            logger.info(
                "auth.verification_code_resent",
                extra={
                    "event": "auth.verification_code_resent",
                    "kind": "signup_resend",
                    "user_id": str(user.id),
                },
            )

            return NayaHttpResponse.no_content()
        except HTTPException:
            metrics.MODULE_ERRORS.labels(module="auth").inc()
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
                metrics.AUTH_FAILURES.labels(reason="unknown_email").inc()
                logger.warning(
                    "auth.login_unknown_email",
                    extra={
                        "event": "auth.login_unknown_email",
                        "email_domain": email.split("@", 1)[1] if "@" in email else "<no-domain>",
                    },
                )
                NayaHttpResponse.unauthorized()

            return user
        except HTTPException as e:
            raise e

        except Exception as e:
            metrics.MODULE_ERRORS.labels(module="auth").inc()
            logger.exception(
                "auth.login_lookup_failed",
                extra={
                    "event": "auth.login_lookup_failed",
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
            )
            NayaHttpResponse.internal_error()

    def verify_user_password(self, user: UserModel, password: str) -> bool:
        is_valid_password = verify_password(
            plain_password=password, hashed_password=user.password
        )

        if not is_valid_password:
            metrics.AUTH_FAILURES.labels(reason="invalid_password").inc()
            logger.warning(
                "auth.login_invalid_password",
                extra={
                    "event": "auth.login_invalid_password",
                    "user_id": str(user.id),
                    "role": user.user_kind.value if user.user_kind else None,
                },
            )
            NayaHttpResponse.unauthorized()

        return True

    async def is_user_verified(self, user: UserModel):
        if not user.is_verified:
            logger.warning(
                "auth.user_not_verified",
                extra={
                    "event": "auth.user_not_verified",
                    "user_id": str(user.id),
                },
            )
            NayaHttpResponse.forbidden(
                data={
                    "message": NayaResponseCodes.UNVERIFIED_USER.detail,
                },
                error_id=NayaResponseCodes.UNVERIFIED_USER.code,
            )

    async def login(self, user: UserModel, password: str):
        try:
            if user.user_kind == UserRoles.PATIENT:
                patient_or_therapist_id = user.patient.id if user.patient else None
            elif user.user_kind == UserRoles.THERAPIST:
                patient_or_therapist_id = (
                    user.therapist.id if user.therapist else None
                )
            else:  # PARENT u otro: no aplica patient_id ni therapist_id
                patient_or_therapist_id = None

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

            metrics.LOGIN_SUCCESS.labels(role=user.user_kind.value).inc()
            logger.info(
                "auth.login_success",
                extra={
                    "event": "auth.login_success",
                    "user_id": str(user.id),
                    "role": user.user_kind.value,
                },
            )

            # Sentry: leave context so future errors for the same user
            # within this or subsequent requests can be correlated.
            sentry.set_user(user_id=str(user.id), role=user.user_kind.value)
            sentry.breadcrumb(
                category="auth",
                message="login.success",
                data={"role": user.user_kind.value},
            )

            return responses.JSONResponse(
                content={
                    "status": "Login success",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user_type": user.user_kind.value,
                }
            )
        except HTTPException as e:
            metrics.AUTH_FAILURES.labels(reason="http_exception").inc()
            logger.warning(
                "auth.login_failed",
                extra={"event": "auth.login_failed", "detail": str(e.detail)},
            )
            raise e

        except Exception as e:
            metrics.AUTH_FAILURES.labels(reason="internal_error").inc()
            metrics.MODULE_ERRORS.labels(module="auth").inc()
            logger.error(
                "auth.login_error",
                extra={"event": "auth.login_error", "error": str(e)},
                exc_info=True,
            )
            NayaHttpResponse.internal_error()

    async def connect_therapist(self, *, token: str, code: str):
        therapist = AuthService.get_therapist_by_code(self.session, code=code)
        user_id = get_user_id_from_token(token)
        if not therapist:
            metrics.THERAPIST_CONNECTION_REJECTED.labels(reason="unknown_code").inc()
            logger.warning(
                "auth.connect_therapist_unknown_code",
                extra={
                    "event": "auth.connect_therapist_unknown_code",
                    "user_id": str(user_id),
                    # NO logueamos el código completo (es token de invitación)
                    "code_prefix": code[:2] if code else None,
                },
            )
            NayaHttpResponse.bad_request(
                data={
                    "message": NayaResponseCodes.UNEXISTING_CODE.detail,
                    "providedValue": {"code": code},
                },
                error_id=NayaResponseCodes.UNEXISTING_CODE.code,
            )

        patient = AuthService.get_patient_by_user_id(self.session, user_id=user_id)
        if not patient:
            metrics.THERAPIST_CONNECTION_REJECTED.labels(reason="unknown_patient").inc()
            logger.warning(
                "auth.connect_therapist_unknown_patient",
                extra={
                    "event": "auth.connect_therapist_unknown_patient",
                    "user_id": str(user_id),
                    "therapist_id": str(therapist.id),
                },
            )
            NayaHttpResponse.bad_request(
                data={
                    "message": NayaResponseCodes.UNEXISTING_PATIENT.detail,
                    "providedValue": {"patient_id": patient.id},
                },
                error_id=NayaResponseCodes.UNEXISTING_PATIENT.code,
            )

        if AuthService.connection_exists(
            self.session, therapist_id=therapist.id, patient_id=patient.id
        ):
            metrics.THERAPIST_CONNECTION_REJECTED.labels(reason="already_linked").inc()
            logger.warning(
                "auth.connect_therapist_already_linked",
                extra={
                    "event": "auth.connect_therapist_already_linked",
                    "therapist_id": str(therapist.id),
                    "patient_id": str(patient.id),
                },
            )
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

        conn = AuthService.create_connection(
            self.session, therapist_id=therapist.id, patient_id=patient.id
        )
        patient.is_connected = True
        self.session.add(patient)
        self.session.commit()

        metrics.PATIENT_THERAPIST_CONNECTIONS.inc()
        logger.info(
            "auth.connection_created",
            extra={
                "event": "auth.connection_created",
                "therapist_id": str(therapist.id),
                "patient_id": str(patient.id),
            },
        )

        # Rare and critical business event → captured as info-level
        # Issue in Sentry.
        sentry.track(
            "patient_therapist.connection.created",
            level="info",
            category="business",
            tags={"event_type": "connection_created"},
            extras={
                "therapist_id": str(therapist.id),
                "patient_id": str(patient.id),
                "connection_id": str(conn.id),
            },
        )

        return NayaHttpResponse.no_content()

    async def get_daily_advice(self) -> AdviceResponse:
        advice = AuthService.get_shared_daily_advice(self.session)
        return AdviceResponse(
            id=advice.id,
            title=advice.title,
            description=advice.description,
        )
