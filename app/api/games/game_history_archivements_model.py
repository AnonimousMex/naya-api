from datetime import datetime, timezone
from uuid import UUID
from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel


class GameHistoryAchievementsModel(BaseNayaModel, table=True):
    __tablename__="game_history_achievements"

    user_id: UUID = Field (foreign_key="users.id", default=None)
    game_id: UUID = Field(foreign_key="games.id", default=None)
    played_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: "UserModel" = Relationship(back_populates="game_history_achivements")   # type: ignore
    game: "GameModel" = Relationship(back_populates="game_history_achivements")  # type: ignore
