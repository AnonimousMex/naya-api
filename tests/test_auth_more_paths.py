"""
Tests para los métodos restantes de AuthController:
- get_verification_code_by_code
- request_password_reset_verification_code
- resend_code
- update_user_password
- login (warning paths)
- get_daily_advice
- get_current_user (con verified=False)
- select_profile_picture
- verify_code

Todo mockeado: session, AuthService, UserService, EmailService.
"""
import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.auth.auth_controller import AuthController
from app.api.auth.auth_model import VerificationCodeModel
from app.constants.user_constants import UserRoles


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _user(verified=True, role=UserRoles.PATIENT):
    user = SimpleNamespace()
    user.id = uuid4()
    user.email = "u@y.com"
    user.name = "tester"
    user.password = "hashed"
    user.is_verified = verified
    user.user_kind = role
    user.patient = None
    user.therapist = None
    return user


# --- get_verification_code_by_code -----------------------------------------


class TestGetVerificationCodeByCode:
    def test_unknown_code_raises_400(self):
        ctrl = AuthController(session=MagicMock())
        request = SimpleNamespace(code="UNKNOWN")
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc:
            async def _none(*a, **kw):
                return None
            fake_svc.get_verification_code.side_effect = _none

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.get_verification_code_by_code(request=request))
            assert exc.value.status_code == 400

    def test_known_code_returns_it(self):
        ctrl = AuthController(session=MagicMock())
        request = SimpleNamespace(code="KNOWN")
        code_obj = SimpleNamespace(code="KNOWN", is_alive=True)
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc:
            async def _ret(*a, **kw):
                return code_obj
            fake_svc.get_verification_code.side_effect = _ret

            result = _run(ctrl.get_verification_code_by_code(request=request))
            assert result is code_obj


# --- request_password_reset_verification_code ------------------------------


class TestRequestPasswordReset:
    def test_creates_when_no_existing_record(self):
        ctrl = AuthController(session=MagicMock())
        user = _user()
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc, \
             patch("app.api.auth.auth_controller.EmailService") as fake_email:
            async def _gen(*a, **kw):
                return "NEWCODE"
            async def _exists(*a, **kw):
                return False
            async def _create(*a, **kw):
                return SimpleNamespace(code="NEWCODE")
            async def _send(*a, **kw):
                return None
            fake_svc.generate_unique_verification_code.side_effect = _gen
            fake_svc.user_in_the_verification_codes_tables.side_effect = _exists
            fake_svc.create_verification_code_reset_password.side_effect = _create
            fake_email.send_verification_email.side_effect = _send

            response = _run(ctrl.request_password_reset_verification_code(user=user))
            assert response is not None
            fake_svc.create_verification_code_reset_password.assert_called_once()
            fake_svc.update_verification_code_reset_password.assert_not_called()

    def test_updates_when_existing_record(self):
        ctrl = AuthController(session=MagicMock())
        user = _user()
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc, \
             patch("app.api.auth.auth_controller.EmailService") as fake_email:
            async def _gen(*a, **kw):
                return "NEWCODE"
            async def _exists(*a, **kw):
                return True
            async def _update(*a, **kw):
                return SimpleNamespace(code="NEWCODE")
            async def _send(*a, **kw):
                return None
            fake_svc.generate_unique_verification_code.side_effect = _gen
            fake_svc.user_in_the_verification_codes_tables.side_effect = _exists
            fake_svc.update_verification_code_reset_password.side_effect = _update
            fake_email.send_verification_email.side_effect = _send

            _run(ctrl.request_password_reset_verification_code(user=user))
            fake_svc.update_verification_code_reset_password.assert_called_once()


# --- update_user_password --------------------------------------------------


class TestUpdateUserPassword:
    def test_calls_service_and_returns_no_content(self):
        ctrl = AuthController(session=MagicMock())
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc:
            async def _update(*a, **kw):
                return None
            fake_svc.update_user_password.side_effect = _update

            response = _run(ctrl.update_user_password(user_id=uuid4(), password="newpw"))
            assert response is not None
            fake_svc.update_user_password.assert_called_once()


# --- resend_code -----------------------------------------------------------


class TestResendCode:
    def test_generates_and_sends_email(self):
        ctrl = AuthController(session=MagicMock())
        user = _user()
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc, \
             patch("app.api.auth.auth_controller.EmailService") as fake_email:
            async def _gen(*a, **kw):
                return "RESEND123"
            async def _update(*a, **kw):
                return SimpleNamespace(code="RESEND123")
            async def _send(*a, **kw):
                return None
            fake_svc.generate_unique_verification_code.side_effect = _gen
            fake_svc.update_verification_code.side_effect = _update
            fake_email.send_verification_email.side_effect = _send

            _run(ctrl.resend_code(user=user))
            fake_email.send_verification_email.assert_called_once()


# --- login (warning paths) -------------------------------------------------


class TestLoginWarningPaths:
    def test_login_success_for_patient(self):
        ctrl = AuthController(session=MagicMock())
        user = _user(role=UserRoles.PATIENT)
        user.patient = SimpleNamespace(id=uuid4(), animal_id=None)

        with patch("app.api.auth.auth_controller.get_user_token") as fake_token:
            fake_token.return_value = "fake-jwt"
            response = _run(ctrl.login(user=user, password="any"))
            # Es JSONResponse, debería tener .status_code o .body
            assert response is not None

    def test_login_success_for_therapist(self):
        ctrl = AuthController(session=MagicMock())
        user = _user(role=UserRoles.THERAPIST)
        user.therapist = SimpleNamespace(id=uuid4(), code_conection="ABC")

        with patch("app.api.auth.auth_controller.get_user_token") as fake_token:
            fake_token.return_value = "fake-jwt"
            response = _run(ctrl.login(user=user, password="any"))
            assert response is not None

    def test_login_success_for_parent(self):
        # PARENT no tiene patient_id ni therapist_id
        ctrl = AuthController(session=MagicMock())
        user = _user(role=UserRoles.PARENT)

        with patch("app.api.auth.auth_controller.get_user_token") as fake_token:
            fake_token.return_value = "fake-jwt"
            response = _run(ctrl.login(user=user, password="any"))
            assert response is not None


# --- get_daily_advice ------------------------------------------------------


class TestGetDailyAdvice:
    def test_returns_advice_response(self):
        ctrl = AuthController(session=MagicMock())
        advice = SimpleNamespace(
            id=uuid4(), title="Be kind", description="...", created_at=None
        )
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc:
            fake_svc.get_shared_daily_advice.return_value = advice

            result = _run(ctrl.get_daily_advice())
            assert result.id == advice.id
            assert result.title == "Be kind"


# --- get_current_user not verified -----------------------------------------


class TestGetCurrentUserNotVerified:
    def test_unverified_user_raises_403(self):
        ctrl = AuthController(session=MagicMock())
        user = _user(verified=False)
        with patch("app.api.auth.auth_controller.UserService") as fake_user_svc:
            async def _ret_user(*a, **kw):
                return user
            fake_user_svc.get_user_by_email.side_effect = _ret_user
            with pytest.raises(HTTPException) as exc:
                _run(ctrl.get_current_user(email="u@y.com"))
            assert exc.value.status_code == 403


# --- verify_code -----------------------------------------------------------


class TestVerifyCodeFlow:
    def test_verify_code_path_signup(self):
        ctrl = AuthController(session=MagicMock())
        code = MagicMock(spec=VerificationCodeModel)
        code.user_id = uuid4()
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc, \
             patch("app.api.auth.auth_controller.UserService") as fake_user_svc:
            async def _ok(*a, **kw):
                return None
            fake_svc.update_verification_code_status.side_effect = _ok
            fake_user_svc.verify_user.side_effect = _ok

            response = _run(ctrl.verify_code(verification_code_model=code))
            assert response is not None
            fake_user_svc.verify_user.assert_called_once()

    def test_verify_code_path_password_reset(self):
        # Cuando el modelo no es VerificationCodeModel, va al path de password reset.
        ctrl = AuthController(session=MagicMock())
        # Modelo distinto: SimpleNamespace cualquiera (no VerificationCodeModel).
        code = SimpleNamespace()
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc:
            async def _ok(*a, **kw):
                return None
            fake_svc.update_verification_code_status.side_effect = _ok

            response = _run(ctrl.verify_code(verification_code_model=code))
            assert response is not None


# --- select_profile_picture -----------------------------------------------


class TestSelectProfilePicture:
    def test_user_not_found_raises_404(self):
        ctrl = AuthController(session=MagicMock())
        request = SimpleNamespace(user_id=uuid4(), id_animal=uuid4())
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc:
            fake_svc.assign_animal.return_value = None
            with pytest.raises(HTTPException) as exc:
                _run(ctrl.select_profile_picture(request=request))
            assert exc.value.status_code == 404

    def test_success_returns_no_content(self):
        ctrl = AuthController(session=MagicMock())
        request = SimpleNamespace(user_id=uuid4(), id_animal=uuid4())
        with patch("app.api.auth.auth_controller.AuthService") as fake_svc:
            fake_svc.assign_animal.return_value = SimpleNamespace(id=uuid4())
            response = _run(ctrl.select_profile_picture(request=request))
            assert response is not None
