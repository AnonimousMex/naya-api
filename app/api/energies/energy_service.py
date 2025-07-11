from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlmodel import Session, select

from app.api.energies.energy_model import EnergyModel


class EnergyService:
    @staticmethod
    async def recharge_energy(
        session: Session, user_id: UUID
    ):
        #En pruebas print()
        statement = select(EnergyModel).where(EnergyModel.user_id == user_id)
        energy = session.exec(statement).first()
        if not energy:
            raise ValueError("User energy configuration not found")

        now = datetime.now(timezone.utc)
        elapsed_time = now - energy.last_charge
        minutes_elapsed = elapsed_time.total_seconds() / 60

        # Calcular energía a recargar
        energy_to_add = int(minutes_elapsed // energy.recharge_time)
        
        if energy_to_add > 0:
            # Actualizar energía
            energy.current_energy = min(
                energy.max_energy,
                energy.current_energy + energy_to_add
            )
            
            # Actualizar tiempo de última recarga
            energy.last_charge = energy.last_charge + timedelta(
                minutes=energy_to_add * energy.recharge_time
            )
            session.add(energy)
            session.commit()
        
        return