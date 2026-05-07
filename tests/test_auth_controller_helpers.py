"""
Tests para los métodos puros del AuthController que no requieren DB:
- verify_user_password
- is_user_verified
- verify_is_code_alive

Mockeamos la session para los métodos que la usan, sin llegar a Postgres.
"""
import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.auth.auth_controller import AuthController
from app.constants.user_constants import UserRoles
from app.utils.security import get_password_hash


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _user(*, email="x@y.com", password_plain="hunter2", verified=True, role=UserRoles.PATIENT):
    user = SimpleNamespace()
    user.id = "11111111-1111-1111-1111-111111111111"
    user.email = email
    user.name = "Tester"
    user.password = get_password_hash(password_plain)
    user.is_verified = verified
    user.user_kind = role
    user.patient = None
    user.therapist = None
    return user


class TestVerifyUserPassword:
    def test_correct_password_returns_true(self):
        ctrl = AuthController(session=MagicMock())
        user = _user(password_plain="rightpass")
        assert ctrl.verify_user_password(user=user, password="rightpass") is True

    def test_wrong_password_raises_401(self):
        ctrl = AuthController(session=MagicMock())
        user = _user(password_plain="rightpass")
        with pytest.raises(HTTPException) as exc:
            ctrl.verify_user_password(user=user, password="WRONG")
        assert exc.value.status_code == 401


class TestIsUserVerified:
    def test_verified_user_passes_silently(self):
        ctrl = AuthController(session=MagicMock())
        user = _user(verified=True)
        # No debe levantar nada.
        _run(ctrl.is_user_verified(user=user))

    def test_unverified_user_raises_403(self):
        ctrl = AuthController(session=MagicMock())
        user = _user(verified=False)
        with pytest.raises(HTTPException) as exc:
            _run(ctrl.is_user_verified(user=user))
        assert exc.value.status_code == 403


class TestVerifyIsCodeAlive:
    def test_alive_code_returns_true(self):
        ctrl = AuthController(session=MagicMock())
        code = SimpleNamespace(is_alive=True, code="ABC123")
        assert ctrl.verify_is_code_alive(code) is True

    def test_dead_code_raises_400(self):
        ctrl = AuthController(session=MagicMock())
        code = SimpleNamespace(is_alive=False, code="USED99")
        with pytest.raises(HTTPException) as exc:
            ctrl.verify_is_code_alive(code)
        assert exc.value.status_code == 400


class TestGetCurrentUserFromLogin:
    def test_unknown_email_raises_401(self):
        ctrl = AuthController(session=MagicMock())
        with patch("app.api.auth.auth_controller.UserService") as fake_svc:
            # get_user_by_email retorna False cuando no encuentra al user.
            async def _ret_false(*a, **kw):
                return False
            fake_svc.get_user_by_email.side_effect = _ret_false

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.get_current_user_from_login(email="ghost@x.com"))
            assert exc.value.status_code == 401

    def test_known_email_returns_user(self):
        ctrl = AuthController(session=MagicMock())
        user = _user(email="real@x.com")

        async def _ret_user(*a, **kw):
            return user

        with patch("app.api.auth.auth_controller.UserService") as fake_svc:
            fake_svc.get_user_by_email.side_effect = _ret_user
            result = _run(ctrl.get_current_user_from_login(email="real@x.com"))
            assert result is user
