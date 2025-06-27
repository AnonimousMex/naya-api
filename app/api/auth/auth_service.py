from random import randint
from typing import Union
from uuid import UUID

from sqlmodel import Session, select

from app.api.patients.patient_model import PatientModel
from app.api.pictures.picture_animal_emotion_model import PictureAnimalEmotionModel
from app.api.pictures.picture_model import PictureModel
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
    async def generate_unique_verification_code(
        session: Session, model: VerificationModels
    ) -> str:
        try:
            while True:
                code_digits = [randint(0, 9) for _ in range(4)]
                code = "".join(map(str, code_digits))
                # if model == "VerificationCodeModel":
                existing_code = session.exec(
                    select(VerificationCodeModel).where(
                        VerificationCodeModel.code == code
                    )
                ).first()
                # else:
                    # existing_code = session.exec(
                    #     select(VerificationCodePasswordResetModel).where(
                    #         VerificationCodePasswordResetModel.code == code
                    #     )
                    # ).first()

                if not existing_code:
                    return code
        except Exception as e:
            print(e)
            NayaHttpResponse.internal_error()
    @staticmethod
    async def create_verification_code(
        code: str,
        user_id: UUID,
        session: Session,
    ) -> VerificationCodeModel:
        try:
            user = VerificationCodeModel(code=code, user_id=user_id)

            session.add(user)
            session.commit()
            session.refresh(user)

            return user
        except Exception:
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


@staticmethod
def assign_animal_and_picture(
    session: Session,
    user_id: UUID,
    id_picture: UUID,
    id_animal: UUID,
    id_emotion: UUID,
) -> PictureAnimalEmotionModel | None:
    try:
        picture_stmt = select(PictureModel).where(
            PictureModel.id == id_picture, PictureModel.is_profile == True
        )
        picture = session.exec(picture_stmt).first()
        if not picture:
            return None

        patient_stmt = select(PatientModel).where(PatientModel.user_id == user_id)
        patient = session.exec(patient_stmt).first()
        if not patient:
            return None

        relation = PictureAnimalEmotionModel(
            id_picture=id_picture, id_animal=id_animal, id_emotion=id_emotion
        )
        session.add(relation)

        patient.animal_id = id_animal
        session.add(patient)

        session.commit()
        session.refresh(relation)

        return relation

    except Exception:
        NayaHttpResponse.internal_error()