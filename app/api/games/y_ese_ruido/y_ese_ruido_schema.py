from pydantic import BaseModel


class GameSoundsResponse(BaseModel):
    audio_path: str
    emotion: str
    title: str
    body: str
    tip: str
    highlight: str

