from uuid import UUID
from sqlmodel import Session, select
from app.core.http_response import NayaHttpResponse
from uuid import UUID
from app.api.badges.badge_model import BadgeModel, UserBadgeModel
from app.api.badges.badge_schema import BadgeResponseModel



class BadgeService:

    @staticmethod
    async def unlock_badge(session: Session, user_id: UUID, badge_title: str) -> BadgeModel:
        try:

            statement = select(BadgeModel).where(BadgeModel.title == badge_title)
            badge = session.exec(statement).first()

            if not badge:
                raise NayaHttpResponse.not_found("Badge not found")
        

            new_user_badge = UserBadgeModel(user_id=user_id, badge_id=badge.id)

            session.add(new_user_badge)
            session.commit()
            session.refresh(new_user_badge)

            return {
                "title": badge.title,
                "description": badge.description,
                "image_path": badge.image_path,
            }

        except Exception as e:
            raise NayaHttpResponse.internal_error()
        
    @staticmethod
    async def badge_exists(
    session: Session, *, user_id: UUID, badge_title: str
    ) -> bool:
        
        statement = select(BadgeModel).where(BadgeModel.title == badge_title)
        badge = session.exec(statement).first()
    
        if not badge:
            return False

        stmt = select(UserBadgeModel).where(
            UserBadgeModel.user_id == user_id,
            UserBadgeModel.badge_id == badge.id,
        )

        result = session.exec(stmt).first()

        return result is not None
    
    
    @staticmethod
    def get_badges(session: Session, user_id: str) -> list[BadgeResponseModel]:
        statement = (
            select(BadgeModel)
            .join(UserBadgeModel, BadgeModel.id == UserBadgeModel.badge_id)
            .where(UserBadgeModel.user_id == user_id)
        )

        try:
            results = session.exec(statement).all()
        except Exception as e:
            raise

        try:
            response = [
                BadgeResponseModel(
                    title=badge.title,
                    description=badge.description,  
                    image_path=badge.image_path,
                )
                for badge in results
            ]
            return response
        except Exception as e:
            raise

