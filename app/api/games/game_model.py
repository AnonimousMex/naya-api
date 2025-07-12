# from datetime import datetime
# from typing import List
# from sqlmodel import Field, Relationship
# from app.core.base_model import BaseNayaModel

# class GameModel(BaseNayaModel, table=True):
#     __tablename__="games"

#     name: str = Field(max_length=40, nullable=False)
#     description: str = Field(max_length=70, nullable=False)
#     image_url: str = Field(nullable=False)
#     deleted_at: datetime = Field(default_factory=None, nullable=True)

#     game_history_achivements: List["GameHistoryAchievementsModel"]  = Relationship(back_populates="game")  # type: ignore
