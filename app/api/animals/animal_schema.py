from pydantic import BaseModel
from typing import Optional

class AnimalResponseSchema(BaseModel):
    animal_id: str
    name: str
    description: str
    color_ui: str
    happy_profile_picture: Optional[str]
