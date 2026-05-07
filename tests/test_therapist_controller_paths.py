"""
Tests para los métodos de TherapistController, con session y servicios
mockeados.
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


def _therapist():
    user_dump = SimpleNamespace(
        id=uuid4(),
        name="Dr. Test",
        email="t@x.com",
        last_name="Test",
        animal=None,
    )
    return SimpleNamespace(
        id=uuid4(),
        user=SimpleNamespace(
            id=uuid4(), email="t@x.com", name="Dr Test"
        ),
    )


# --- get_therapist_by_id ---------------------------------------------------


class TestGetTherapistById:
    def test_not_found_raises_404(self):
        ctrl = TherapistController(session=MagicMock())
        with patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc:
            async def _none(*a, **kw):
                return None
            fake_svc.get_therapist_by_id.side_effect = _none

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.get_therapist_by_id(therapist_id=uuid4()))
            assert exc.value.status_code == 404


# --- create_appointment ---------------------------------------------------


class TestCreateAppointment:
    def test_conflict_raises_400(self):
        ctrl = TherapistController(session=MagicMock())
        with patch("app.api.therapists.therapist_controller.AuthService") as fake_auth, \
             patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc, \
             patch("app.api.therapists.therapist_controller.get_user_id_from_token") as fake_uid:
            fake_uid.return_value = "user-1"
            fake_auth.get_therapist_by_user_id.return_value = SimpleNamespace(id=uuid4())
            fake_svc.appointment_exists.return_value = True

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.create_appointment(
                    token="t", patient_id=uuid4(),
                    date=date(2026, 6, 1), time=time(10, 0),
                ))
            assert exc.value.status_code == 400


# --- cancel_appointment ---------------------------------------------------


class TestCancelAppointment:
    def test_calls_service_returns_no_content(self):
        ctrl = TherapistController(session=MagicMock())
        with patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc:
            fake_svc.cancel_appointment.return_value = None
            response = _run(ctrl.cancel_appointment(appointment_id=uuid4()))
            assert response is not None
            fake_svc.cancel_appointment.assert_called_once()


# --- list_appointments ----------------------------------------------------


class TestListAppointments:
    def test_empty_raises_404(self):
        ctrl = TherapistController(session=MagicMock())
        with patch("app.api.therapists.therapist_controller.AuthService") as fake_auth, \
             patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc, \
             patch("app.api.therapists.therapist_controller.get_user_id_from_token") as fake_uid:
            fake_uid.return_value = "user-1"
            fake_auth.get_therapist_by_user_id.return_value = SimpleNamespace(id=uuid4())
            async def _empty(*a, **kw):
                return []
            fake_svc.list_appointments.side_effect = _empty

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.list_appointments(token="t"))
            assert exc.value.status_code == 404

    def test_returns_appointments(self):
        ctrl = TherapistController(session=MagicMock())
        with patch("app.api.therapists.therapist_controller.AuthService") as fake_auth, \
             patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc, \
             patch("app.api.therapists.therapist_controller.get_user_id_from_token") as fake_uid:
            fake_uid.return_value = "user-1"
            fake_auth.get_therapist_by_user_id.return_value = SimpleNamespace(id=uuid4())
            async def _list(*a, **kw):
                return [SimpleNamespace(id=uuid4())]
            fake_svc.list_appointments.side_effect = _list

            result = _run(ctrl.list_appointments(token="t"))
            assert len(result) == 1


# --- reschedule_appointment ----------------------------------------------


class TestRescheduleAppointment:
    def test_conflict_raises_400(self):
        ctrl = TherapistController(session=MagicMock())
        with patch("app.api.therapists.therapist_controller.AuthService") as fake_auth, \
             patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc, \
             patch("app.api.therapists.therapist_controller.get_user_id_from_token") as fake_uid:
            fake_uid.return_value = "user-1"
            fake_auth.get_therapist_by_user_id.return_value = SimpleNamespace(id=uuid4())
            fake_svc.appointment_exists.return_value = True

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.reschedule_appointment(
                    token="t", appointment_id=uuid4(),
                    date=date(2026, 6, 1), time=time(10, 0),
                ))
            assert exc.value.status_code == 400

    def test_no_conflict_succeeds(self):
        ctrl = TherapistController(session=MagicMock())
        with patch("app.api.therapists.therapist_controller.AuthService") as fake_auth, \
             patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc, \
             patch("app.api.therapists.therapist_controller.get_user_id_from_token") as fake_uid:
            fake_uid.return_value = "user-1"
            fake_auth.get_therapist_by_user_id.return_value = SimpleNamespace(id=uuid4())
            fake_svc.appointment_exists.return_value = False

            response = _run(ctrl.reschedule_appointment(
                token="t", appointment_id=uuid4(),
                date=date(2026, 6, 1), time=time(10, 0),
            ))
            assert response is not None


# --- complete_appointment ------------------------------------------------


class TestCompleteAppointment:
    def test_calls_service(self):
        ctrl = TherapistController(session=MagicMock())
        with patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc:
            fake_svc.complete_appointment.return_value = None
            response = _run(ctrl.complete_appointment(appointment_id=uuid4()))
            assert response is not None
            fake_svc.complete_appointment.assert_called_once()


# --- disconnect_patient --------------------------------------------------


class TestDisconnectPatient:
    def test_therapist_not_found_raises_404(self):
        ctrl = TherapistController(session=MagicMock())
        with patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc:
            async def _none(*a, **kw):
                return None
            fake_svc.get_therapist_by_id.side_effect = _none

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.disconnect_patient(
                    therapist_id=uuid4(), patient_id=uuid4()
                ))
            assert exc.value.status_code == 404

    def test_patient_not_found_raises_404(self):
        ctrl = TherapistController(session=MagicMock())
        with patch("app.api.therapists.therapist_controller.AuthService") as fake_auth, \
             patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc:
            async def _therapist(*a, **kw):
                return SimpleNamespace(id=uuid4())
            fake_svc.get_therapist_by_id.side_effect = _therapist
            fake_auth.get_patient.return_value = None

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.disconnect_patient(
                    therapist_id=uuid4(), patient_id=uuid4()
                ))
            assert exc.value.status_code == 404

    def test_no_existing_connection_raises_400(self):
        ctrl = TherapistController(session=MagicMock())
        with patch("app.api.therapists.therapist_controller.AuthService") as fake_auth, \
             patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc:
            async def _therapist(*a, **kw):
                return SimpleNamespace(id=uuid4())
            fake_svc.get_therapist_by_id.side_effect = _therapist
            fake_auth.get_patient.return_value = SimpleNamespace(
                id=uuid4(), is_connected=True
            )
            fake_auth.connection_exists.return_value = False

            with pytest.raises(HTTPException) as exc:
                _run(ctrl.disconnect_patient(
                    therapist_id=uuid4(), patient_id=uuid4()
                ))
            assert exc.value.status_code == 400


# --- list_patients --------------------------------------------------------


class TestListPatients:
    def test_empty_raises_404(self):
        ctrl = TherapistController(session=MagicMock())
        with patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc:
            async def _empty(*a, **kw):
                return []
            fake_svc.list_patients_by_therapist.side_effect = _empty
            with pytest.raises(HTTPException) as exc:
                _run(ctrl.list_patients(therapist_id=uuid4()))
            assert exc.value.status_code == 404

    def test_returns_patients(self):
        ctrl = TherapistController(session=MagicMock())
        with patch("app.api.therapists.therapist_controller.TherapistService") as fake_svc:
            async def _list(*a, **kw):
                return [SimpleNamespace(id=uuid4())]
            fake_svc.list_patients_by_therapist.side_effect = _list
            result = _run(ctrl.list_patients(therapist_id=uuid4()))
            assert len(result) == 1
