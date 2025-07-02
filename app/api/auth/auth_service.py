from datetime import datetime, timezone
from random import randint
from typing import Union
from uuid import UUID

from sqlmodel import Session, select

from app.api.auth.auth_schema import ResetPasswordRequest
from app.api.patients.patient_model import PatientModel
from app.api.pictures.picture_animal_emotion_model import PictureAnimalEmotionModel
from app.api.pictures.picture_model import PictureModel
from app.api.therapists.therapist_model import TherapistModel
from app.api.users.user_model import UserModel
from app.constants.user_constants import VerificationModels
from app.utils.security import get_password_hash

from .auth_model import (
    ConnectionModel,
    VerificationCodeModel,
    VerificationCodePasswordResetModel,
)

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
            else:
                statement = select(VerificationCodePasswordResetModel).where(
                    VerificationCodePasswordResetModel.code == code
                )

                result = session.exec(statement).first()

            return result
        except Exception:
            NayaHttpResponse.internal_error()

    @staticmethod
    async def user_in_the_verification_codes_tables(
        session: Session,
        user_id: UUID,
        model: Union[VerificationCodeModel, VerificationCodePasswordResetModel],
    ) -> VerificationCodeModel | bool:
        try:
            if isinstance(model, VerificationCodeModel):
                statement = select(VerificationCodeModel).where(
                    VerificationCodeModel.user_id == user_id
                )
            else:
                statement = select(VerificationCodePasswordResetModel).where(
                    VerificationCodePasswordResetModel.user_id == user_id
                )
            result = session.exec(statement).first()

            return result if result else False
        except Exception:
            NayaHttpResponse.internal_error()

    @staticmethod
    async def generate_unique_conection_code(session: Session) -> str:
        try:
            while True:
                code_digits = [randint(0, 9) for _ in range(4)]
                code = "".join(map(str, code_digits))

                existing_code = session.exec(
                    select(TherapistModel).where(TherapistModel.code_conection == code)
                ).first()

                if not existing_code:
                    return code
        except Exception:
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
    async def create_conection_code(
        code: str,
        user_id: UUID,
        session: Session,
    ) -> TherapistModel:
        try:
            therapist = (
                session.query(TherapistModel)
                .filter(TherapistModel.user_id == user_id)
                .first()
            )

            if not therapist:
                raise NayaHttpResponse.internal_error()

            # Actualiza solo el campo code_conection
            therapist.code_conection = code

            session.commit()
            session.refresh(therapist)

            return therapist
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
    async def generate_unique_verification_code(
        session: Session, model: VerificationModels
    ) -> str:
        try:
            while True:
                code_digits = [randint(0, 9) for _ in range(4)]
                code = "".join(map(str, code_digits))
                if model == "VerificationCodeModel":
                    existing_code = session.exec(
                        select(VerificationCodeModel).where(
                            VerificationCodeModel.code == code
                        )
                    ).first()
                else:
                    existing_code = session.exec(
                        select(VerificationCodePasswordResetModel).where(
                            VerificationCodePasswordResetModel.code == code
                        )
                    ).first()

                if not existing_code:
                    return code
        except Exception:
            NayaHttpResponse.internal_error()

    @staticmethod
    async def create_verification_code_reset_password(
        code: str,
        user_id: UUID,
        session: Session,
    ) -> VerificationCodePasswordResetModel:
        try:
            user = VerificationCodePasswordResetModel(code=code, user_id=user_id)

            session.add(user)
            session.commit()
            session.refresh(user)

            return user
        except Exception:
            NayaHttpResponse.internal_error()

    @staticmethod
    async def update_user_password(
        session: Session, user_id: UUID, password: str

    ):
        try:
            hashed_password = get_password_hash(password)
            statement = select(UserModel).where(UserModel.id == user_id)

            user = session.exec(statement).first()
            user.password = hashed_password
            user.updated_at = datetime.now(timezone.utc)

            session.add(user)
            session.commit()
        except Exception:
            NayaHttpResponse.internal_error()

    @staticmethod
    async def update_verification_code_reset_password(
        code: str,
        user_id: UUID,
        session: Session,
    ) -> VerificationCodePasswordResetModel:
        try:
            statement = select(VerificationCodePasswordResetModel).where(
                VerificationCodePasswordResetModel.user_id == user_id
            )

            user = session.exec(statement).first()
            user.code = code
            user.is_alive = True
            user.updated_at = datetime.now(timezone.utc)

            session.add(user)
            session.commit()

            return user
        except Exception:
            NayaHttpResponse.internal_error()

    @staticmethod
    async def update_verification_code(
        code: str,
        user_id: UUID,
        session: Session,
    ) -> VerificationCodeModel:
        try:
            statement = select(VerificationCodeModel).where(
                VerificationCodeModel.user_id == user_id
            )

            user = session.exec(statement).first()
            user.code = code
            user.is_alive = True
            user.updated_at = datetime.now(timezone.utc)

            session.add(user)
            session.commit()

            return user
        except Exception:
            NayaHttpResponse.internal_error()

    @staticmethod
    def get_patient(session: Session, *, patient_id: UUID) -> PatientModel | None:
        return session.get(PatientModel, patient_id)

    @staticmethod
    def connection_exists(
        session: Session, *, therapist_id: UUID, patient_id: UUID
    ) -> bool:
        stmt = select(ConnectionModel).where(
            ConnectionModel.therapist_id == therapist_id,
            ConnectionModel.patient_id == patient_id,
        )
        return session.exec(stmt).first() is not None

    @staticmethod
    def create_connection(
        session: Session, *, therapist_id: UUID, patient_id: UUID
    ) -> ConnectionModel:
        conn = ConnectionModel(therapist_id=therapist_id, patient_id=patient_id)
        session.add(conn)
        session.commit()
        session.refresh(conn)
        return conn

    @staticmethod
    def get_therapist_by_code(session: Session, *, code: str) -> TherapistModel | None:
        stmt = select(TherapistModel).where(TherapistModel.code_conection == code)
        return session.exec(stmt).first()

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
