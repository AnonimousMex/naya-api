from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlmodel import Session, select

from app.api.energies.energy_model import EnergyModel
from app.core.http_response import NayaHttpResponse

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
                return new_energies
            print(energies)
            return energies
        except Exception as e:
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
            
            return
        except Exception as e:
            raise e
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
        except Exception:
            NayaHttpResponse.internal_error()