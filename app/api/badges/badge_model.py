from sqlmodel import Field
from app.core.base_model import BaseNayaModel
from uuid import UUID



class BadgeModel(BaseNayaModel, table=True):
    __tablename__ = "badges"

    title: str = Field(default=None)
    description: str = Field(default=None)
    image_path: str = Field(default=None)

class UserBadgeModel(BaseNayaModel, table=True):
    __tablename__ = "user_badges"

    user_id: UUID = Field(foreign_key="users.id")
    badge_id: UUID = Field(foreign_key="badges.id")

