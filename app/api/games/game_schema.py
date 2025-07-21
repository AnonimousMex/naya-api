from uuid import UUID
from pydantic import BaseModel


class GameListResponse(BaseModel):
    id: UUID
    name: str
    description: str
    image_url: str