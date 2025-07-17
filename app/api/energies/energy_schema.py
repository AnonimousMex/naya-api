from pydantic import BaseModel


class EnergyReponseSchema(BaseModel):
    current_energy: int

    model_config = {"from_attributes": True}