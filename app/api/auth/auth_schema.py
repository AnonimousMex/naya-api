from uuid import UUID
from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class VerificationRequest(BaseModel):
    code: str

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class SelectProfileRequest(BaseModel):
    user_id: UUID
    id_picture: UUID
    id_animal: UUID
    id_emotion: UUID

    class Config:
        alias_generator = to_camel
        populate_by_name = True
