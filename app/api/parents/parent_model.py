from uuid import UUID

from sqlmodel import Field

from app.core.base_model import BaseNayaModel


class ParentChildModel(BaseNayaModel, table=True):
    """
    Relación entre un usuario tutor (UserModel con user_kind=PARENT) y un
    paciente/niño (PatientModel). Un tutor puede tener varios niños y un niño
    puede tener varios tutores.
    """
    __tablename__ = "parent_child"

    parent_user_id: UUID = Field(foreign_key="users.id", nullable=False)
    patient_id: UUID = Field(foreign_key="patients.id", nullable=False)
