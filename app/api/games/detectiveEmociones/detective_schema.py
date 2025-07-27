from typing import List
from uuid import UUID
from app.core.base_model import BaseNayaModel

class AnswerOptions(BaseNayaModel):
    id: UUID
    name: str

class DetectiveSituationsResponse(BaseNayaModel):
    id: UUID
    title: str
    story: str
    emotion_id: UUID
    emotion_name: str
    options: List[AnswerOptions]