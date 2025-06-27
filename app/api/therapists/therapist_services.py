
from sqlmodel import Session
from app.api.therapists.therapist_model import TherapistModel
from app.api.users.user_model import UserModel
from app.core.http_response import NayaHttpResponse


class TherapistService: 
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


