from uuid import UUID
from sqlmodel import Field
from app.core.base_model import BaseNayaModel


class SoundsGameSoundsModel(BaseNayaModel, table=True):
    __tablename__ = "sounds_game_sounds"

    audio_path: str = Field(default=None)
    emotion_id: UUID = Field(foreign_key="emotions.id")
   
class SoundsGameCluesModel(BaseNayaModel, table= True):
    __tablename__ = "sounds_game_clues"

    title: str = Field(default=None)
    body: str = Field(default=None)
    tip: str = Field(default=None)
    highlight: str = Field(default=None)
    sound_id: UUID = Field(foreign_key="sounds_game_sounds.id")
    
