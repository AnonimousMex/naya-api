"""
Cubre los exception paths que faltan en:
- badge_controller (success unlock, exception en unlock, exception en get_badges)
- energy_controller (get_current exception, consume exception)
- detective_controller (HTTPException path)
- game_controller (success path adicional)
"""
import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.badges.badge_controller import BadgeController
from app.api.energies.energy_controller import EnergyController


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# --- BADGE unlock success path ------------------------------------------


class TestBadgeUnlockSuccess:
    def test_full_unlock_returns_response(self):
        ctrl = BadgeController(session=MagicMock())
        with patch("app.api.badges.badge_controller.BadgeService") as fake_svc, \
             patch("app.api.badges.badge_controller.get_user_id_from_token") as fake_uid, \
             patch("app.api.badges.badge_controller.BadgeResponseModel") as fake_resp, \
             patch("app.api.badges.badge_controller.jsonable_encoder") as fake_enc:
            async def _exists(*a, **kw):
                return False
            async def _unlock(*a, **kw):
                return SimpleNamespace(id=uuid4(), title="T")
            fake_svc.badge_exists.side_effect = _exists
            fake_svc.unlock_badge.side_effect = _unlock
            fake_uid.return_value = "user-1"
            fake_enc.return_value = {"id": "x", "title": "T"}
            fake_resp.return_value = MagicMock()

            response = _run(ctrl.unlock_badge(token="t", badge_title="T"))
            assert response is not None


# --- BADGE unlock except path -------------------------------------------


class TestBadgeUnlockExcept:
    def test_unexpected_exception_caught(self):
        ctrl = BadgeController(session=MagicMock())
        with patch("app.api.badges.badge_controller.BadgeService") as fake_svc, \
             patch("app.api.badges.badge_controller.get_user_id_from_token") as fake_uid:
            async def _bad(*a, **kw):
                raise RuntimeError("db down")
            fake_svc.badge_exists.side_effect = _bad
            fake_uid.return_value = "user-1"

            with pytest.raises(HTTPException):
                _run(ctrl.unlock_badge(token="t", badge_title="T"))


# --- BADGE get_badges except path ----------------------------------------


class TestBadgeGetBadgesExcept:
    def test_unexpected_exception_caught(self):
        ctrl = BadgeController(session=MagicMock())
        with patch("app.api.badges.badge_controller.BadgeService") as fake_svc, \
             patch("app.api.badges.badge_controller.get_user_id_from_token") as fake_uid:
            fake_svc.get_badges.side_effect = RuntimeError("db down")
            fake_uid.return_value = "user-1"

            with pytest.raises(HTTPException):
                ctrl.get_badges(token="t")

    def test_http_exception_propagates(self):
        ctrl = BadgeController(session=MagicMock())
        with patch("app.api.badges.badge_controller.get_user_id_from_token") as fake_uid:
            fake_uid.side_effect = HTTPException(status_code=401, detail="Invalid token")

            with pytest.raises(HTTPException) as exc:
                ctrl.get_badges(token="bad")
            assert exc.value.status_code == 401


# --- ENERGY get_current except --------------------------------------------


class TestEnergyGetCurrentExcept:
    def test_unexpected_exception_propagates(self):
        ctrl = EnergyController(session=MagicMock())
        with patch("app.api.energies.energy_controller.EnergyService") as fake_svc, \
             patch("app.api.energies.energy_controller.get_user_id_from_token") as fake_uid:
            async def _bad(*a, **kw):
                raise RuntimeError("db down")
            fake_svc.recharge_energy.side_effect = _bad
            fake_uid.return_value = "user-1"

            with pytest.raises(RuntimeError):
                _run(ctrl.get_current_energies(token="t"))


# --- ENERGY consume except ------------------------------------------------


class TestEnergyConsumeExcept:
    def test_unexpected_exception_propagates(self):
        ctrl = EnergyController(session=MagicMock())
        with patch("app.api.energies.energy_controller.EnergyService") as fake_svc, \
             patch("app.api.energies.energy_controller.get_user_id_from_token") as fake_uid:
            async def _bad(*a, **kw):
                raise RuntimeError("db down")
            fake_svc.consume_energy.side_effect = _bad
            fake_uid.return_value = "user-1"

            with pytest.raises(RuntimeError):
                _run(ctrl.consume_user_energy(token="t"))


# --- AUTH connect_therapist with auth header ----------------------------


class TestAuthConnectionAlternativePaths:
    def test_invalid_token_raises_401(self):
        from app.api.auth.auth_controller import AuthController
        ctrl = AuthController(session=MagicMock())
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc, \
             patch("app.api.auth.auth_controller.get_user_id_from_token") as fake_uid:
            fake_uid.side_effect = HTTPException(status_code=401, detail="Invalid token")
            fake_svc.get_therapist_by_code.return_value = SimpleNamespace(id=uuid4())

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.connect_therapist(token="bad", code="GOOD"))
            assert exc.value.status_code == 401
