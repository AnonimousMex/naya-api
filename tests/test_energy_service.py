"""
Tests para EnergyService — la capa que toca SQL contra el modelo
EnergyModel. Mockeamos session.exec(...).first() para no depender de DB.
"""
import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.api.energies.energy_service import EnergyService


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _energy(*, current=2, max_=3, last_charge=None, recharge=15):
    return SimpleNamespace(
        user_id=uuid4(),
        current_energy=current,
        max_energy=max_,
        last_charge=last_charge or datetime.now(timezone.utc),
        recharge_time=recharge,
    )


def _session_with(energy_value):
    """Crea session.exec(...).first() que devuelve energy_value."""
    session = MagicMock()
    exec_result = MagicMock()
    exec_result.first.return_value = energy_value
    session.exec.return_value = exec_result
    return session


# --- get_current_energies -------------------------------------------------


class TestGetCurrentEnergies:
    def test_returns_existing_row(self):
        energy = _energy(current=1)
        session = _session_with(energy)
        result = _run(EnergyService.get_current_energies(session=session, user_id=uuid4()))
        assert result is energy

    def test_creates_new_row_when_missing(self):
        session = _session_with(None)
        # session.refresh es no-op (es un MagicMock — no necesita config)
        result = _run(EnergyService.get_current_energies(session=session, user_id=uuid4()))
        # Devolvió el nuevo objeto que se acabó de añadir
        assert result is not None
        session.add.assert_called_once()
        session.commit.assert_called_once()


# --- recharge_energy ------------------------------------------------------


class TestRechargeEnergy:
    def test_no_row_returns_none(self):
        session = _session_with(None)
        # No debe crashear ni hacer commit.
        result = _run(EnergyService.recharge_energy(session=session, user_id=uuid4()))
        assert result is None
        session.commit.assert_not_called()

    def test_too_recent_no_recharge(self):
        # Última carga hace 1 segundo → no han pasado los 15 min.
        recent = datetime.now(timezone.utc)
        energy = _energy(current=1, last_charge=recent)
        session = _session_with(energy)
        _run(EnergyService.recharge_energy(session=session, user_id=energy.user_id))
        # current_energy NO debe cambiar.
        assert energy.current_energy == 1
        session.commit.assert_not_called()

    def test_enough_time_passed_recharges(self):
        # 30 minutos después → 2 cargas (recharge_time=15).
        old = datetime.now(timezone.utc) - timedelta(minutes=30)
        energy = _energy(current=0, max_=3, last_charge=old, recharge=15)
        session = _session_with(energy)
        _run(EnergyService.recharge_energy(session=session, user_id=energy.user_id))
        # 2 unidades agregadas, capped por max_energy
        assert energy.current_energy == 2
        session.commit.assert_called_once()

    def test_naive_datetime_normalized(self):
        # last_charge sin tzinfo no debe crashear.
        old_naive = datetime.utcnow() - timedelta(minutes=30)
        energy = _energy(current=0, last_charge=old_naive)
        session = _session_with(energy)
        _run(EnergyService.recharge_energy(session=session, user_id=energy.user_id))
        # No raise — pasa sin problema.

    def test_caps_at_max_energy(self):
        old = datetime.now(timezone.utc) - timedelta(hours=2)
        energy = _energy(current=0, max_=3, last_charge=old, recharge=15)
        session = _session_with(energy)
        _run(EnergyService.recharge_energy(session=session, user_id=energy.user_id))
        # Aunque pasaron 8 cargas, no excede el max
        assert energy.current_energy == 3


# --- consume_energy -------------------------------------------------------


class TestConsumeEnergy:
    def test_zero_energy_returns_false(self):
        energy = _energy(current=0, max_=3)
        session = _session_with(energy)
        result = _run(EnergyService.consume_energy(session=session, user_id=energy.user_id))
        assert result is False
        # No se hace commit cuando no hay energía
        session.commit.assert_not_called()

    def test_consume_decrements_and_returns_true(self):
        energy = _energy(current=2, max_=3)
        session = _session_with(energy)
        result = _run(EnergyService.consume_energy(session=session, user_id=energy.user_id))
        assert result is True
        assert energy.current_energy == 1
        session.commit.assert_called_once()

    def test_consuming_max_energy_resets_last_charge(self):
        # Cuando se consume desde el máximo, last_charge se resetea a ahora.
        old = datetime.now(timezone.utc) - timedelta(days=1)
        energy = _energy(current=3, max_=3, last_charge=old)
        session = _session_with(energy)
        _run(EnergyService.consume_energy(session=session, user_id=energy.user_id))
        # last_charge debe haber subido (más reciente que `old`)
        assert energy.last_charge > old
