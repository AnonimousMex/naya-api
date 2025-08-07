from typing import List
from uuid import UUID

from pydantic import BaseModel

class AnswerOptions(BaseModel):
    id: UUID
    name: str
    isCorrect: bool

class DetectiveSituationsResponse(BaseModel):
    id: UUID
    title: str
    story: str
    image:str | None
    options: List[AnswerOptions]