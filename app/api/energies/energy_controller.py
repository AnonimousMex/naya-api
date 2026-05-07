
from fastapi import HTTPException
from sqlmodel import Session

from app.api.energies.energy_schema import EnergyReponseSchema
from app.api.energies.energy_service import EnergyService
from app.constants.response_codes import NayaResponseCodes
from app.core import metrics
from app.core.http_response import NayaHttpResponse
from app.core.logger import logger
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
        except Exception as e:
            metrics.MODULE_ERRORS.labels(module="energy").inc()
            logger.exception(
                "energy.get_current_failed",
                extra={
                    "event": "energy.get_current_failed",
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
            )
            raise

    async def consume_user_energy(self, token: str):
        try:
            user_id = get_user_id_from_token(token)
            consumed = await EnergyService.consume_energy(self.session, user_id=user_id)
            if consumed is False:
                metrics.ENERGY_DEPLETED.inc()
                logger.warning(
                    "energy.depleted",
                    extra={
                        "event": "energy.depleted",
                        "user_id": str(user_id),
                    },
                )
                NayaHttpResponse.bad_request(
                    data={
                        "message": NayaResponseCodes.NO_MORE_LIVES.detail,
                    },
                    error_id=NayaResponseCodes.NO_MORE_LIVES.code,
                )
            metrics.ENERGY_CONSUMED.inc()
            logger.info(
                "energy.consumed",
                extra={"event": "energy.consumed", "user_id": str(user_id)},
            )
            return NayaHttpResponse.no_content()
        except HTTPException as e:
            raise e
        except Exception as e:
            metrics.MODULE_ERRORS.labels(module="energy").inc()
            logger.exception(
                "energy.consume_failed",
                extra={
                    "event": "energy.consume_failed",
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
            )
            raise