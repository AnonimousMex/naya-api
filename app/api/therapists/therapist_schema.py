

from uuid import UUID
from app.api.users.user_schema import UserCreateSchema, UserResponseSchema, UserSchema


class TherapistSchema(UserSchema):
    pass

class TherapistCreateSchema(UserCreateSchema):
    pass

class TherapistResponseSchema(UserResponseSchema):
    therapist_id: UUID