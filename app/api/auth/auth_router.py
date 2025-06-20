from uuid import UUID
from fastapi import APIRouter, HTTPException

from app.api.auth.auth_controller import AuthController

from app.api.auth.auth_schema import VerificationRequest

from app.constants.user_constants import VerificationModels
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
