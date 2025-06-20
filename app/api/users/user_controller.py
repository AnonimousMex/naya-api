

from pydantic import EmailStr
from sqlmodel import Session

from app.api.users.user_service import UserService
from app.constants.response_codes import NayaResponseCodes
from app.core.http_response import NayaHttpResponse


class   UserController:
    def __init__(self, session: Session):
        self.session = session

    async def validate_exixting_user(self, user_email: EmailStr) -> bool:
        user_by_email = await UserService.get_user_by_email(
            email=user_email, session=self.session
        )

        if user_by_email:
            NayaHttpResponse.forbidden(
                data={
                    "message": NayaResponseCodes.EXISTING_EMAIL.detail,
                    "providedValue": user_email,
                },
                error_id=NayaResponseCodes.EXISTING_EMAIL.code,
            )

        return True