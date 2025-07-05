from uuid import UUID
from sqlmodel import Session, select
from app.api.auth.auth_model import ConnectionModel
from app.api.therapists.therapist_model import TherapistModel
from app.api.users.user_model import UserModel
from app.constants.response_codes import NayaResponseCodes
from app.core.http_response import NayaHttpResponse
from app.api.therapists.therapist_schema import TherapistListResponseSchema


class TherapistService:

    @staticmethod
    async def get_therapist_by_id(
        therapist_id: UUID, session: Session
    ) -> TherapistModel | None:
        stmt = select(TherapistModel).where(TherapistModel.id == therapist_id)
        return session.exec(stmt).first()

    @staticmethod
    async def create_therapist(user: UserModel, session: Session) -> TherapistModel:
        try:
            new_therapist = TherapistModel(user=user, user_id=user.id)

            session.add(new_therapist)
            session.commit()
            session.refresh(new_therapist)

            return new_therapist
        except Exception:
            NayaHttpResponse.internal_error()

    @staticmethod
    def delete_connection(session: Session, *, therapist_id: UUID, patient_id: UUID):
        stmt = select(ConnectionModel).where(
            ConnectionModel.therapist_id == therapist_id,
            ConnectionModel.patient_id == patient_id,
        )
        conn = session.exec(stmt).first()
        if conn:
            session.delete(conn)
            session.commit()

    @staticmethod
    async def list_verified_therapists(session) -> list:
        statement = (
            select(TherapistModel)
            .join(UserModel, TherapistModel.user_id == UserModel.id)
            .where(UserModel.is_verified == True)
        )
        results = session.exec(statement).all()
        if not results:
            NayaHttpResponse.not_found(
                data={
                    "message": NayaResponseCodes.NO_VERIFIED_THERAPISTS.detail,
                },
                error_id=NayaResponseCodes.NO_VERIFIED_THERAPISTS.code,
            )
        return [
            TherapistListResponseSchema(
                therapist_id=therapist.id,
                name=therapist.user.name
            )
            for therapist in results
        ]
