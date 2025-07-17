from fastapi import APIRouter, HTTPException, Header

from app.api.energies.energy_controller import EnergyController
from app.api.energies.energy_schema import EnergyReponseSchema
from app.core.database import SessionDep
from app.core.http_response import NayaResponseModel


energy_router = APIRouter(prefix="/energy")

@energy_router.get(
        "/current_energies", 
        response_model=EnergyReponseSchema,
)
async def current_energies(
    session: SessionDep,
    token: str = Header(..., alias="Authorization")
): 
    try:
        energy_controller = EnergyController(session=session)

        return await energy_controller.get_current_energies(token=token)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
    
@energy_router.put("/consume")
async def consume_energy(
    session: SessionDep,
    token: str = Header(..., alias="Authorization")
):
    try:
        energy_controller = EnergyController(session=session)

        return await energy_controller.consume_user_energy(token=token)
    except HTTPException as e:
        raise e