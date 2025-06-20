from uuid import UUID
from datetime import datetime, timezone

from sqlmodel import Session, select

from .user_model import UserModel
from .user_schema import UserCreateSchema

from app.constants.user_constants import UserRoles
from app.utils.security import get_password_hash
from app.core.http_response import NayaHttpResponse


class UserService:
    @staticmethod
    async def create_user(
        user_data: UserCreateSchema, user_kind: UserRoles, session: Session
    ) -> UserModel:
        try:
            hashed_password = get_password_hash(user_data.password)

            user_dump = user_data.model_dump()

            new_user = UserModel(**user_dump, user_kind=user_kind)

            new_user.password = hashed_password

            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            return new_user
        except Exception:
            NayaHttpResponse.internal_error()

    @staticmethod
    async def get_user_by_id(user_id: UUID, session: Session) -> UserModel:
        try:
            statement = select(UserModel).where(UserModel.id == user_id)
            user = session.exec(statement).first()
            return user
        except Exception:
            NayaHttpResponse.internal_error()

    @staticmethod
    async def get_user_by_email(email: str, session: Session) -> UserModel | bool:
        try:
            statement = select(UserModel).where(UserModel.email == email)

            user = session.exec(statement).first()

            return user if user else False
        except Exception as e:
            print(e)
            NayaHttpResponse.internal_error()

    @staticmethod
    async def verify_user(user_id: UUID, session: Session):
        try:
            statement = select(UserModel).where(UserModel.id == user_id)

            user = session.exec(statement).first()
            user.is_verified = True
            user.updated_at = datetime.now(timezone.utc)

            session.add(user)
            session.commit()
        except Exception:
            NayaHttpResponse.internal_error()

    @staticmethod
    async def update_user_password(user_id: UUID, password: str, session: Session):
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
