"""
Tests para los exception paths NO cubiertos de AuthController.
Estos cubren las ramas de `except Exception` que loguean a Sentry y
levantan internal_error.
"""
import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.auth.auth_controller import AuthController


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# --- get_current_user except path -----------------------------------------


class TestGetCurrentUserExceptPath:
    def test_unexpected_exception_raises_500(self):
        ctrl = AuthController(session=MagicMock())
        with patch("app.api.auth.auth_controller.UserService") as fake_svc:
            async def _bad(*a, **kw):
                raise RuntimeError("db down")
            fake_svc.get_user_by_email.side_effect = _bad

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.get_current_user(email="u@y.com"))
            assert exc.value.status_code == 500


# --- verify_code except path ----------------------------------------------


class TestVerifyCodeExceptPath:
    def test_db_error_raises_500(self):
        from app.api.auth.auth_model import VerificationCodeModel
        ctrl = AuthController(session=MagicMock())
        code = MagicMock(spec=VerificationCodeModel)
        code.user_id = uuid4()
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc:
            async def _bad(*a, **kw):
                raise RuntimeError("db down")
            fake_svc.update_verification_code_status.side_effect = _bad

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.verify_code(verification_code_model=code))
            assert exc.value.status_code == 500


# --- select_profile_picture except path ----------------------------------


class TestSelectProfileExceptPath:
    def test_db_error_raises_500(self):
        ctrl = AuthController(session=MagicMock())
        request = SimpleNamespace(user_id=uuid4(), id_animal=uuid4())
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc:
            fake_svc.assign_animal.side_effect = RuntimeError("db boom")
            with pytest.raises(HTTPException) as exc:
                _run(ctrl.select_profile_picture(request=request))
            assert exc.value.status_code == 500


# --- get_current_user_from_login except path ------------------------------


class TestGetCurrentUserFromLoginExceptPath:
    def test_unexpected_exception_raises_500(self):
        ctrl = AuthController(session=MagicMock())
        with patch("app.api.auth.auth_controller.UserService") as fake_svc:
            async def _bad(*a, **kw):
                raise RuntimeError("db down")
            fake_svc.get_user_by_email.side_effect = _bad

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.get_current_user_from_login(email="u@y.com"))
            assert exc.value.status_code == 500


# --- request_password_reset_verification_code except path -----------------


class TestRequestPasswordResetExceptPath:
    def test_unexpected_exception_raises_500(self):
        ctrl = AuthController(session=MagicMock())
        user = SimpleNamespace(
            id=uuid4(), email="u@y.com", name="t", is_verified=True
        )
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc:
            async def _bad(*a, **kw):
                raise RuntimeError("db down")
            fake_svc.generate_unique_verification_code.side_effect = _bad

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.request_password_reset_verification_code(user=user))
            assert exc.value.status_code == 500


# --- update_user_password except path -------------------------------------


class TestUpdateUserPasswordExceptPath:
    def test_http_exception_caught_and_500_raised(self):
        ctrl = AuthController(session=MagicMock())
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc:
            async def _bad(*a, **kw):
                raise HTTPException(status_code=400, detail="bad")
            fake_svc.update_user_password.side_effect = _bad

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.update_user_password(user_id=uuid4(), password="x"))
            # El controller cachea HTTPException y devuelve 500
            assert exc.value.status_code == 500


# --- resend_code except path ----------------------------------------------


class TestResendCodeExceptPath:
    def test_http_exception_caught_returns_500(self):
        ctrl = AuthController(session=MagicMock())
        user = SimpleNamespace(
            id=uuid4(), email="u@y.com", name="t",
        )
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc:
            async def _bad(*a, **kw):
                raise HTTPException(status_code=400, detail="bad")
            fake_svc.generate_unique_verification_code.side_effect = _bad

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.resend_code(user=user))
            assert exc.value.status_code == 500


# --- login except path ----------------------------------------------------


class TestLoginExceptPath:
    def test_unexpected_exception_raises_500(self):
        from app.constants.user_constants import UserRoles

        ctrl = AuthController(session=MagicMock())
        user = SimpleNamespace(
            id=uuid4(), email="u@y.com", name="t",
            user_kind=UserRoles.PATIENT, patient=None,
        )
        with patch("app.api.auth.auth_controller.get_user_token") as fake_token:
            fake_token.side_effect = RuntimeError("jwt boom")
            with pytest.raises(HTTPException) as exc:
                _run(ctrl.login(user=user, password="x"))
            assert exc.value.status_code == 500


# --- connect_therapist success path --------------------------------------


class TestConnectTherapistSuccess:
    def test_full_flow_creates_connection(self):
        ctrl = AuthController(session=MagicMock())
        therapist = SimpleNamespace(id=uuid4())
        patient = SimpleNamespace(id=uuid4(), is_connected=False)
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc, \
             patch("app.api.auth.auth_controller.get_user_id_from_token") as fake_uid:
            fake_uid.return_value = "user-1"
            fake_svc.get_therapist_by_code.return_value = therapist
            fake_svc.get_patient_by_user_id.return_value = patient
            fake_svc.connection_exists.return_value = False
            fake_svc.create_connection.return_value = SimpleNamespace(id=uuid4())

            response = _run(ctrl.connect_therapist(token="t", code="GOOD"))
            assert response is not None
            assert patient.is_connected is True
            ctrl.session.commit.assert_called()
