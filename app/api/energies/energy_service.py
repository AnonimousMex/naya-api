from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlmodel import Session, select

from app.api.energies.energy_model import EnergyModel
from app.core import metrics
from app.core.http_response import NayaHttpResponse
from app.core.logger import logger

class EnergyService:
    @staticmethod
    async def get_current_energies( session: Session, user_id: UUID):
        try:
            statement = select(EnergyModel).where(EnergyModel.user_id == user_id)
            energies = session.exec(statement).first()
            if not energies:
                new_energies = EnergyModel(user_id=user_id)
                session.add(new_energies)
                session.commit()
                session.refresh(new_energies)
                logger.info(
                    "energy.row_initialized",
                    extra={
                        "event": "energy.row_initialized",
                        "user_id": str(user_id),
                    },
                )
                return new_energies
            return energies
        except Exception as e:
            logger.exception(
                "energy.get_current_db_failed",
                extra={
                    "event": "energy.get_current_db_failed",
                    "user_id": str(user_id),
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
            )
            raise e

    @staticmethod
    async def recharge_energy(
        session: Session, user_id: UUID
    ):
        try:
            statement = select(EnergyModel).where(EnergyModel.user_id == user_id)
            energy = session.exec(statement).first()
            if not energy:
                return

            now = datetime.now(timezone.utc)
            if energy.last_charge.tzinfo is None or energy.last_charge.tzinfo.utcoffset(energy.last_charge) is None:
                energy.last_charge = energy.last_charge.replace(tzinfo=timezone.utc)
            elapsed_time = now - energy.last_charge
            minutes_elapsed = elapsed_time.total_seconds() / 60

            energy_to_add = int(minutes_elapsed // energy.recharge_time)
            if energy_to_add > 0:
                energy.current_energy = min(
                    energy.max_energy,
                    energy.current_energy + energy_to_add
                )

                energy.last_charge = energy.last_charge + timedelta(
                    minutes=energy_to_add * energy.recharge_time
                )
                session.add(energy)
                session.commit()
                metrics.ENERGY_RECHARGED_UNITS.inc(energy_to_add)
                logger.info(
                    "energy.recharged",
                    extra={
                        "event": "energy.recharged",
                        "user_id": str(user_id),
                        "added": energy_to_add,
                        "current_energy": energy.current_energy,
                    },
                )

            return
        except Exception as e:
            logger.exception(
                "energy.recharge_failed",
                extra={
                    "event": "energy.recharge_failed",
                    "user_id": str(user_id),
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
            )
            NayaHttpResponse.internal_error()

    @staticmethod
    async def consume_energy(session: Session, user_id:UUID):
        try:
            statement = select(EnergyModel).where(EnergyModel.user_id == user_id)
            energy = session.exec(statement).first()
            if energy.current_energy == 0:
                return False
            if energy.current_energy == energy.max_energy:
                energy.last_charge = datetime.now(timezone.utc)
            energy.current_energy = energy.current_energy - 1
            session.add(energy)
            session.commit()
            session.refresh(energy)
            return True
        except Exception as e:
            logger.exception(
                "energy.consume_db_failed",
                extra={
                    "event": "energy.consume_db_failed",
                    "user_id": str(user_id),
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
            )
            NayaHttpResponse.internal_error()