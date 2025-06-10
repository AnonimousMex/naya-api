from abc import ABC
from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


class BaseNayaModel(ABC, SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
