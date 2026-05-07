
from fastapi import HTTPException
from sqlmodel import Session

from app.api.energies.energy_schema import EnergyReponseSchema
from app.api.energies.energy_service import EnergyService
from app.constants.response_codes import NayaResponseCodes
from app.core.http_response import NayaHttpResponse
from app.utils.security import decode_token, get_user_id_from_token


class EnergyController:
    def __init__(self, session: Session):
        self.session = session

    async def get_current_energies(self, token: str):
        try:
            user_id = get_user_id_from_token(token)
            await EnergyService.recharge_energy(self.session, user_id=user_id)
            energies = await EnergyService.get_current_energies(self.session, user_id=user_id)

            return EnergyReponseSchema(
                current_energy=energies.current_energy
            )
        except HTTPException as e:
            raise e

    async def consume_user_energy(self, token: str):
        try:
            user_id = get_user_id_from_token(token)
            if await EnergyService.consume_energy(self.session, user_id=user_id) == False:
                NayaHttpResponse.bad_request(
                    data={
                        "message": NayaResponseCodes.NO_MORE_LIVES.detail,
                    },
                    error_id=NayaResponseCodes.NO_MORE_LIVES.code,
                )
            return NayaHttpResponse.no_content()
        except HTTPException as e:
            raise e