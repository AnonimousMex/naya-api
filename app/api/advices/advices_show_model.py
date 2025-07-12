from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel


class AdvicesShownModel(BaseNayaModel, table=True):
    __tablename__="advices_shown"

    advice_id: UUID = Field(foreign_key="advices.id")
    date_shown: datetime = Field(nullable=False)

    advice: "AdviceModel" = Relationship(back_populates="advices_shown") # type: ignore