from sqlmodel import Field
from app.constants.user_constants import ActivityTypes
from app.core.base_model import BaseNayaModel


class ActivityModel(BaseNayaModel, table=True):
    __tablename__="activities"

    title: str = Field(max_length=20, nullable=False)
    description: str = Field(max_length=80, nullable=False)
    image_url: str = Field(nullable=False)
    type: ActivityTypes
