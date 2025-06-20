from typing import Union
from uuid import UUID

from sqlmodel import Session, select

from app.constants.user_constants import VerificationModels

from .auth_model import VerificationCodeModel

from app.core.http_response import NayaHttpResponse


class AuthService:
    @staticmethod
    async def get_verification_code(
        code: str, table: VerificationModels, session: Session
    ) -> VerificationCodeModel:
        try:
            if table == VerificationModels.VERIFICATION_CODE_MODEL:
                statement = select(VerificationCodeModel).where(
                    VerificationCodeModel.code == code
                )

                result = session.exec(statement).first()

                return result
        except Exception:
            NayaHttpResponse.internal_error()

    @staticmethod
    async def user_in_the_verification_code_table(
        session: Session, user_id: UUID
    ) -> VerificationCodeModel | bool:
        try:
            statement = select(VerificationCodeModel).where(
                VerificationCodeModel.user_id == user_id
            )

            result = session.exec(statement).first()

            return result if result else False
        except Exception as e:
            NayaHttpResponse.internal_error()

    @staticmethod
    async def update_verification_code_status(
        verification_code: Union[VerificationCodeModel],
        session: Session,
    ):
        try:
            if isinstance(verification_code, VerificationCodeModel):
                verification_code.is_alive = False
                session.add(verification_code)
                session.commit()
            else:
                verification_code.is_alive = False
                session.add(verification_code)
                session.commit()
        except Exception:
            NayaHttpResponse.internal_error()
