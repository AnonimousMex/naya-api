from datetime import datetime, timezone
import enum
from typing import Union
from uuid import UUID
from random import randint

from sqlmodel import Session, select

from app.api.therapists.therapist_model import TherapistModel
from app.constants.user_constants import VerificationModels


from app.core.http_response import NayaHttpResponse


class AuthService:
    # @staticmethod
    # async def create_verification_code(
    #     code: str,
    #     user_id: UUID,
    #     session: Session,
    # ) -> VerificationCodeModel:
    #     try:
    #         verification_code = VerificationCodeModel(code=code, user_id=user_id)

    #         session.add(verification_code)
    #         session.commit()
    #         session.refresh(verification_code)

    #         return verification_code
    #     except Exception:
    #         NayaHttpResponse.internal_error()

    # @staticmethod
    # async def create_verification_code_reset_password(
    #     code: str,
    #     user_id: UUID,
    #     session: Session,
    # ) -> VerificationCodePasswordResetModel:
    #     try:
    #         user = VerificationCodePasswordResetModel(code=code, user_id=user_id)

    #         session.add(user)
    #         session.commit()
    #         session.refresh(user)

    #         return user
    #     except Exception:
    #         NayaHttpResponse.internal_error()

    # @staticmethod
    # async def update_verification_code_reset_password(
    #     code: str,
    #     user_id: UUID,
    #     session: Session,
    # ) -> VerificationCodePasswordResetModel:
    #     try:
    #         statement = select(VerificationCodePasswordResetModel).where(
    #             VerificationCodePasswordResetModel.user_id == user_id
    #         )

    #         user = session.exec(statement).first()
    #         user.code = code
    #         user.is_alive = True
    #         user.updated_at = datetime.now(timezone.utc)

    #         session.add(user)
    #         session.commit()

    #         return user
    #     except Exception:
    #         NayaHttpResponse.internal_error()


    @staticmethod
    async def generate_unique_code_conection(
        session: Session
    ) -> str:
        try:
            while True:
                code_digits = [randint(0, 9) for _ in range(4)]
                code = "".join(map(str, code_digits))
                existing_code = session.exec(
                    select(TherapistModel).where(
                        TherapistModel.code==code
                    ).first()
                )
                if not existing_code:
                    return code
        except Exception:
            NayaHttpResponse.internal_error()


    # @staticmethod
    # async def generate_unique_verification_code(
    #     session: Session, model: VerificationModels
    # ) -> str:
    #     try:
    #         while True:
    #             code_digits = [randint(0, 9) for _ in range(4)]
    #             code = "".join(map(str, code_digits))
    #             if model == "VerificationCodeModel":
    #                 existing_code = session.exec(
    #                     select(VerificationCodeModel).where(
    #                         VerificationCodeModel.code == code
    #                     )
    #                 ).first()
    #             else:
    #                 existing_code = session.exec(
    #                     select(VerificationCodePasswordResetModel).where(
    #                         VerificationCodePasswordResetModel.code == code
    #                     )
    #                 ).first()

    #             if not existing_code:
    #                 return code
    #     except Exception:
    #         NayaHttpResponse.internal_error()

    # @staticmethod
    # async def get_verification_code(
    #     code: str, table: VerificationModels, session: Session
    # ) -> VerificationCodeModel | VerificationCodePasswordResetModel:
    #     try:
    #         if(table == VerificationModels.VERIFICATION_CODE_MODEL):
    #             statement = select(VerificationCodeModel).where(
    #                 VerificationCodeModel.code == code
    #             )

    #             result = session.exec(statement).first()

    #             return result
    #         else:
    #             statement = select(VerificationCodePasswordResetModel).where(
    #                 VerificationCodePasswordResetModel.code == code
    #             )

    #             result = session.exec(statement).first()

    #             return result
    #     except Exception:
    #         NayaHttpResponse.internal_error()

    # @staticmethod
    # async def user_in_the_verification_code_password_reset_table(
    #     session: Session, user_id: UUID
    # ) -> VerificationCodeModel | bool:
    #     try:
    #         statement = select(VerificationCodePasswordResetModel).where(
    #             VerificationCodePasswordResetModel.user_id == user_id
    #         )

    #         result = session.exec(statement).first()
    #         return result if result else False
    #     except Exception as e:
    #         NayaHttpResponse.internal_error()

    # @staticmethod
    # async def update_verification_code_status(
    #     verification_code: Union[VerificationCodeModel, VerificationCodePasswordResetModel], session: Session
    # ):
    #     try:
    #         if isinstance(verification_code, VerificationCodeModel):
    #             verification_code.is_alive = False
    #             session.add(verification_code)
    #             session.commit()
    #         else:
    #             verification_code.is_alive = False
    #             session.add(verification_code)
    #             session.commit()
    #     except Exception:
    #         NayaHttpResponse.internal_error()
