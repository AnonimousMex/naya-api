from uuid import UUID
from fastapi import APIRouter, HTTPException

from app.api.auth.auth_controller import AuthController

from app.api.auth.auth_schema import VerificationRequest, SelectProfileRequest
import traceback


from app.constants.user_constants import VerificationModels
from app.core.database import SessionDep
import logging
import traceback

logger = logging.getLogger("uvicorn.error")


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


@auth_router.post("/select-profile")
async def select_profile_picture(request: SelectProfileRequest, session: SessionDep):
    try:
        auth_controller = AuthController(session=session)
        return await auth_controller.select_profile_picture(request)

    except HTTPException as e:
        raise e

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
