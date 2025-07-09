from uuid import UUID
from fastapi import APIRouter, HTTPException

from app.api.auth.auth_controller import AuthController

from app.api.auth.auth_schema import (
    RequestPasswordChange,
    ResendCode,
    ConnectionCodeRequest,
    VerificationRequest,
    SelectProfileRequest,
)

from app.api.auth.auth_service import AuthService
from app.constants.user_constants import VerificationModels
from app.core.auth import LoginFormDataDep
from app.core.database import SessionDep


auth_router = APIRouter(prefix="/auth")


@auth_router.post("/verification-code")
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

    except Exception as e:
        raise e


@auth_router.post("/password-change-request")
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

    except Exception as e:
        raise e


@auth_router.post("/verification-code-password-reset")
async def verify_code(request: VerificationRequest, session: SessionDep):
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

    except Exception as e:
        raise e


@auth_router.post("/connect-therapist")
async def connect_therapist(request: ConnectionCodeRequest, session: SessionDep):
    try:
        auth_controller = AuthController(session=session)
        return await auth_controller.connect_therapist(
            patient_id=request.id_patient,
            code=request.code,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e


@auth_router.post("/select-profile")
async def select_profile_picture(request: SelectProfileRequest, session: SessionDep):
    try:
        auth_controller = AuthController(session=session)
        return await auth_controller.select_profile_picture(request)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e


@auth_router.put("/resend-verification-code")
async def resend_verification_code(request: ResendCode, session: SessionDep):
    try:
        auth_controller = AuthController(session=session)

        current_user = await auth_controller.get_current_user_from_login(
            email=request.email
        )

        return await auth_controller.resend_code(user=current_user)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise e


@auth_router.post("/login")
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

    except Exception as e:
        raise e
