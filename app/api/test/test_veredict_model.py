from uuid import UUID
from sqlmodel import Field, Relationship
from app.core.base_model import BaseNayaModel


class TestVeredictModel(BaseNayaModel, table=True):
    __tablename__= "test_veredict"

    test_id: UUID = Field(foreign_key="tests.id", nullable=False)
    veredict_id: UUID = Field(foreign_key="veredicts.id", nullable=False)

    test: "TestModel" = Relationship(back_populates="testVeredict") # type: ignore
    veredict: "VeredictModel" = Relationship(back_populates="testVeredict") # type: ignore