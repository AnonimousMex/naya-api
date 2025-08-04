from typing import List
from uuid import UUID

from pydantic import BaseModel
from app.core.base_model import BaseNayaModel

class AnswerOptions(BaseModel):
    id: UUID
    name: str
    isCorrect: bool

class DetectiveSituationsResponse(BaseModel):
    id: UUID
    title: str
    story: str
    options: List[AnswerOptions]