from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Field
from app.core.base_model import BaseNayaModel


class EnergyModel(BaseNayaModel, table=True):
    __tablename__="energies"

    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    current_energy: int = Field(nullable=False, default=3, ge=0)
    max_energy: int = Field(nullable=False, default=3)
    last_charge: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    recharge_time: int = Field(default=30)

