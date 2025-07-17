from uuid import UUID
from pydantic import BaseModel


class MemocionPairResponse(BaseModel):
    pair_id: UUID
    emotion: str
    situation: str
