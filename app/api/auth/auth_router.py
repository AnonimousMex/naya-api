from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Header, Request

from app.api.auth.auth_controller import AuthController
from app.api.auth.auth_dependencies import get_current_patient_id
from app.api.auth.auth_schema import (
    AdviceResponse,
    RequestPasswordChange,
    ResendCode,
    ConnectionCodeRequest,
    ResetPasswordRequest,
    VerificationRequest,
    SelectProfileRequest,
)

from app.api.auth.auth_service import AuthService
from app.constants.user_constants import VerificationModels
from app.core.auth import LoginFormDataDep, oauth, oauth2_access_token
from app.core.database import SessionDep
from app.core.settings import settings
from app.core.http_response import NayaHttpResponse
from app.utils.rate_limiter import rate_limiter

auth_router = APIRouter(prefix="/auth")


@auth_router.get("/google/login", dependencies=[Depends(rate_limiter)])
async def google_login(request: Request):
    try:
        return await oauth.google.authorize_redirect(
            request, settings.GOOGLE_REDIRECT_URI
        )
    except Exception:
        NayaHttpResponse.internal_error()


@auth_router.get("/google/callback")
async def google_callback(request: Request, session: SessionDep):
    try:
        auth_controller = AuthController(session=session)
        return await auth_controller.authenticate_external_user(
            request=request, provider="google"
        )
    except HTTPException as e:
        raise e
    except Exception:
        NayaHttpResponse.internal_error()


@auth_router.get("/github/login", dependencies=[Depends(rate_limiter)])
async def github_login(request: Request):
    try:
        return await oauth.github.authorize_redirect(
            request, settings.GITHUB_REDIRECT_URI
        )
    except Exception:
        NayaHttpResponse.internal_error()


@auth_router.get("/github/callback")
async def github_callback(request: Request, session: SessionDep):
    try:
        auth_controller = AuthController(session=session)
        return await auth_controller.authenticate_external_user(
            request=request, provider="github"
        )
    except HTTPException as e:
        raise e
    except Exception:
        NayaHttpResponse.internal_error()


@auth_router.post("/login", dependencies=[Depends(rate_limiter)])
async def login(session: SessionDep, form_data: LoginFormDataDep):
    try:
        email = form_data.username
        password = form_data.password
        auth_controller = AuthController(session)
        current_user = await auth_controller.get_current_user_from_login(email=email)
        auth_controller.verify_user_password(user=current_user, password=password)
        await auth_controller.is_user_verified(user=current_user)
        return await auth_controller.login(user=current_user, password=password)
    except HTTPException as e:
        raise e
    except Exception:
        NayaHttpResponse.internal_error()


@auth_router.post("/verification-code", dependencies=[Depends(rate_limiter)])
async def verify_user_verification_code(
    request: VerificationRequest, session: SessionDep
):
    try:
        auth_controller = AuthController(session=session)
        verification_code = await auth_controller.get_verification_code_by_code(
            request=request, model=VerificationModels.VERIFICATION_CODE_MODEL
        )
        auth_controller.verify_is_code_alive(verification_code=verification_code)
        return await auth_controller.verify_code(
            verification_code_model=verification_code
        )
    except HTTPException as e:
        raise e
    except Exception:
        NayaHttpResponse.internal_error()


@auth_router.post("/password-change-request", dependencies=[Depends(rate_limiter)])
async def request_password_reset_verification_code(
    request: RequestPasswordChange, session: SessionDep
):
    try:
        auth_controller = AuthController(session=session)
        user_verified = await auth_controller.get_current_user(email=request.email)
        return await auth_controller.request_password_reset_verification_code(
            user=user_verified
        )
    except HTTPException as e:
        raise e
    except Exception:
        NayaHttpResponse.internal_error()


@auth_router.post("/verification-code-password-reset")
async def verify_code_password_reset(request: VerificationRequest, session: SessionDep):
    try:
        auth_controller = AuthController(session=session)
        verification_code = await auth_controller.get_verification_code_by_code(
            request=request,
            model=VerificationModels.VERIFICATION_CODE_PASSWORD_RESET_MODEL,
        )
        auth_controller.verify_is_code_alive(verification_code=verification_code)
        return await auth_controller.verify_code(
            verification_code_model=verification_code
        )
    except HTTPException as e:
        raise e
    except Exception:
        NayaHttpResponse.internal_error()


@auth_router.put("/password-reset")
async def reset_password(request: ResetPasswordRequest, session: SessionDep):
    try:
        auth_controller = AuthController(session=session)
        user = await auth_controller.get_current_user(email=request.email)
        return await auth_controller.update_user_password(
            user_id=user.id, password=request.password
        )
    except HTTPException as e:
        raise e
    except Exception:
        NayaHttpResponse.internal_error()


@auth_router.post("/connect-patient-with-therapist")
async def connect_therapist(
    request: ConnectionCodeRequest,
    session: SessionDep,
    token: str = Header(..., alias="Authorization"),
):
    try:
        auth_controller = AuthController(session=session)
        return await auth_controller.connect_therapist(token=token, code=request.code)
    except HTTPException as e:
        raise e
    except Exception:
        NayaHttpResponse.internal_error()


@auth_router.post("/select-profile")
async def select_profile_picture(request: SelectProfileRequest, session: SessionDep):
    try:
        auth_controller = AuthController(session=session)
        return await auth_controller.select_profile_picture(request)
    except HTTPException as e:
        raise e
    except Exception:
        NayaHttpResponse.internal_error()


@auth_router.put("/resend-verification-code", dependencies=[Depends(rate_limiter)])
async def resend_verification_code(request: ResendCode, session: SessionDep):
    try:
        auth_controller = AuthController(session=session)
        current_user = await auth_controller.get_current_user_from_login(
            email=request.email
        )
        return await auth_controller.resend_code(user=current_user)
    except HTTPException as e:
        raise e
    except Exception:
        NayaHttpResponse.internal_error()


@auth_router.get("/daily", response_model=AdviceResponse)
async def get_daily_advice(
    session: SessionDep,
    token: str = Depends(oauth2_access_token),
):
    try:
        controller = AuthController(session)
        return await controller.get_daily_advice()
    except HTTPException as e:
        raise e
    except Exception:
        NayaHttpResponse.internal_error()


@auth_router.get("/debug-env-poc")
async def debug_environment_poc():
    try:

        provocar_caida = 1 / 0
    except Exception as e:
        import os

        return {
            "status": "vulnerable_debug_active",
            "exception_type": type(e).__name__,
            "exception_message": str(e),
            "file_exposed": os.path.abspath(__file__),
            "exposed_db_user": (
                settings.DB_USER
                if hasattr(settings, "DB_USER")
                else os.getenv("DB_USER")
            ),
            "exposed_jwt_secret": (
                settings.SECRET_KEY
                if hasattr(settings, "SECRET_KEY")
                else "EXPOSED_TOKEN_SECRET"
            ),
            "remediation": "Desactivar modo DEBUG y usar NayaHttpResponse.internal_error() globalmente.",
        }
