"""
Tests adicionales para TherapistController:
- create_therapist (todo el happy path con mocks)
- create_therapist exception path
- get_therapist_by_id success path
- create_appointment success path
- disconnect_patient success path
"""
import asyncio
from datetime import date, time
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.therapists.therapist_controller import TherapistController


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _therapist_data():
    return SimpleNamespace(
        email="dr@x.com", password="hunter2",
        name="Doctor", last_name="Test",
        phone="555-555", description="Bio",
        street="St 1", city="MX", state="CDMX",
        postal_code="01000", animal_id=None,
    )


def _user_obj():
    return SimpleNamespace(
        id=uuid4(), email="dr@x.com", name="doctor",
        last_name="Test", animal=None,
        is_verified=False, user_kind=SimpleNamespace(value="THERAPIST"),
    )


# --- create_therapist ----------------------------------------------------


class TestCreateTherapist:
    def test_happy_path(self):
        ctrl = TherapistController(session=MagicMock())
        td = _therapist_data()
        user = _user_obj()
        therapist = SimpleNamespace(id=uuid4(), user=user)
        v_code = SimpleNamespace(code="ABC123", code_conection=None)
        c_code = SimpleNamespace(code="X", code_conection="CONN9")

        with patch("app.api.therapists.therapist_controller.UserController") as fake_user_ctrl_cls, \
             patch("app.api.therapists.therapist_controller.UserService") as fake_user_svc, \
             patch("app.api.therapists.therapist_controller.TherapistService") as fake_t_svc, \
             patch("app.api.therapists.therapist_controller.AuthService") as fake_auth, \
             patch("app.api.therapists.therapist_controller.EmailService") as fake_email, \
             patch("app.api.therapists.therapist_controller.UserResponseSchema") as fake_resp_schema, \
             patch("app.api.therapists.therapist_controller.TherapistResponseSchema") as fake_t_resp, \
             patch("app.api.therapists.therapist_controller.sentry"):
            user_ctrl = MagicMock()
            async def _validate(*a, **kw):
                return None
            user_ctrl.validate_exixting_user.side_effect = _validate
            fake_user_ctrl_cls.return_value = user_ctrl

            async def _ret_user(*a, **kw):
                return user
            fake_user_svc.create_user.side_effect = _ret_user

            async def _ret_t(*a, **kw):
                return therapist
            fake_t_svc.create_therapist.side_effect = _ret_t

            async def _gen(*a, **kw):
                return "GENERATED"
            fake_auth.generate_unique_verification_code.side_effect = _gen
            fake_auth.generate_unique_conection_code.side_effect = _gen

            async def _vc(*a, **kw):
                return v_code
            fake_auth.create_verification_code.side_effect = _vc

            async def _cc(*a, **kw):
                return c_code
            fake_auth.create_conection_code.side_effect = _cc

            async def _send(*a, **kw):
                return None
            fake_email.send_verification_email.side_effect = _send
            fake_email.send_conection_code_email.side_effect = _send

            # Mock schemas para que no validen pydantic
            fake_resp_schema.model_validate.return_value.model_dump.return_value = {
                "id": user.id, "email": user.email, "name": user.name,
            }
            fake_t_resp.return_value = MagicMock()

            response = _run(ctrl.create_therapist(therapist_data=td))
            assert response is not None
            fake_t_svc.create_therapist.assert_called_once()
            # Ambos emails deben enviarse
            fake_email.send_verification_email.assert_called_once()
            fake_email.send_conection_code_email.assert_called_once()

    def test_validation_exception_propagates(self):
        ctrl = TherapistController(session=MagicMock())
        td = _therapist_data()

        with patch("app.api.therapists.therapist_controller.UserController") as fake_user_ctrl_cls:
            user_ctrl = MagicMock()
            async def _bad(*a, **kw):
                raise HTTPException(status_code=409, detail="email exists")
            user_ctrl.validate_exixting_user.side_effect = _bad
            fake_user_ctrl_cls.return_value = user_ctrl

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.create_therapist(therapist_data=td))
            assert exc.value.status_code == 409


# --- get_therapist_by_id success ------------------------------------------


class TestGetTherapistByIdSuccess:
    def test_returns_response(self):
        ctrl = TherapistController(session=MagicMock())
        therapist = SimpleNamespace(
            id=uuid4(),
            user=SimpleNamespace(
                id=uuid4(), email="t@x.com", name="Doc",
                last_name="Test", animal=None,
                is_verified=True, user_kind=SimpleNamespace(value="THERAPIST"),
            ),
        )
        with patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc, \
             patch("app.api.therapists.therapist_controller.UserResponseSchema") as fake_schema, \
             patch("app.api.therapists.therapist_controller.TherapistResponseSchema") as fake_t_resp:
            async def _ret(*a, **kw):
                return therapist
            fake_svc.get_therapist_by_id.side_effect = _ret
            fake_schema.model_validate.return_value.model_dump.return_value = {
                "id": therapist.user.id, "email": "t@x.com", "name": "Doc",
            }
            fake_t_resp.return_value = MagicMock()

            response = _run(ctrl.get_therapist_by_id(therapist_id=therapist.id))
            assert response is not None


# --- create_appointment success ------------------------------------------


class TestCreateAppointmentSuccess:
    def test_no_conflict_returns_response(self):
        ctrl = TherapistController(session=MagicMock())
        therapist = SimpleNamespace(id=uuid4())
        appointment = SimpleNamespace(
            id=uuid4(), therapist_id=therapist.id, patient_id=uuid4(),
            date=date(2026, 6, 1), time=time(10, 0), status="SCHEDULED",
        )
        with patch("app.api.therapists.therapist_controller.AuthService") as fake_auth, \
             patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc, \
             patch("app.api.therapists.therapist_controller.get_user_id_from_token") as fake_uid, \
             patch("app.api.therapists.therapist_controller.AppointmentResponse") as fake_resp:
            fake_uid.return_value = "user-1"
            fake_auth.get_therapist_by_user_id.return_value = therapist
            fake_svc.appointment_exists.return_value = False
            async def _schedule(*a, **kw):
                return appointment
            fake_svc.schedule_appointment.side_effect = _schedule
            fake_resp.return_value = MagicMock()

            response = _run(ctrl.create_appointment(
                token="t", patient_id=uuid4(),
                date=date(2026, 6, 1), time=time(10, 0),
            ))
            assert response is not None


# --- disconnect_patient success ------------------------------------------


class TestDisconnectPatientSuccess:
    def test_full_disconnect_flow(self):
        ctrl = TherapistController(session=MagicMock())
        therapist = SimpleNamespace(id=uuid4())
        patient = SimpleNamespace(id=uuid4(), is_connected=True)

        with patch("app.api.therapists.therapist_controller.AuthService") as fake_auth, \
             patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc:
            async def _therapist(*a, **kw):
                return therapist
            fake_svc.get_therapist_by_id.side_effect = _therapist
            fake_auth.get_patient.return_value = patient
            fake_auth.connection_exists.return_value = True
            fake_svc.delete_connection.return_value = None

            response = _run(ctrl.disconnect_patient(
                therapist_id=therapist.id, patient_id=patient.id
            ))
            assert response is not None
            # patient.is_connected debe quedar en False
            assert patient.is_connected is False
            ctrl.session.add.assert_called()
            ctrl.session.commit.assert_called()
