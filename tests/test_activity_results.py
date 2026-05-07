"""
Tests para ActivityResultsController.create_result con session mockeada.
Cubre la creación con/sin score, con/sin completed_at, y caminos de
breadcrumb/track de Sentry.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.test.activity_results_controller import ActivityResultsController


def _payload(*, score=None, duration=None, answers=None, completed_at=None):
    return SimpleNamespace(
        child_id=uuid4(),
        activity_id=uuid4(),
        score=score,
        duration_seconds=duration,
        answers=answers or [],
        completed_at=completed_at,
    )


def _patient():
    return SimpleNamespace(id=uuid4(), user_id=uuid4())


class TestCreateResult:
    def _ctrl(self, patient=None, test_id=None):
        session = MagicMock()
        session.get.return_value = patient
        ctrl = ActivityResultsController(session=session)
        # Mock _insert_answers para que no haga DB
        ctrl._insert_answers = MagicMock(return_value=0)
        return ctrl, session

    def test_child_not_found_raises_404(self):
        ctrl, _ = self._ctrl(patient=None)
        with pytest.raises(HTTPException) as exc:
            ctrl.create_result(payload=_payload())
        assert exc.value.status_code == 404

    def test_minimal_payload_creates_open_result(self):
        ctrl, session = self._ctrl(patient=_patient())
        # Mock TestModel para no tocar DB real
        with patch("app.api.test.activity_results_controller.TestModel") as fake_test_cls:
            test_obj = SimpleNamespace(id=uuid4())
            fake_test_cls.return_value = test_obj

            ctrl.create_result(payload=_payload())

            session.add.assert_called()
            assert session.commit.call_count >= 2
            session.refresh.assert_called()

    def test_with_score_sets_completed_at(self):
        ctrl, session = self._ctrl(patient=_patient())
        with patch("app.api.test.activity_results_controller.TestModel") as fake_test_cls:
            test_obj = SimpleNamespace(id=uuid4())
            fake_test_cls.return_value = test_obj

            ctrl.create_result(payload=_payload(score=95, duration=120))

            # completed_at no debe ser None cuando hay score
            kwargs = fake_test_cls.call_args.kwargs
            assert kwargs["completed_at"] is not None
            assert kwargs["score"] == 95

    def test_low_score_triggers_sentry_track(self):
        ctrl, session = self._ctrl(patient=_patient())
        with patch("app.api.test.activity_results_controller.TestModel") as fake_test_cls, \
             patch("app.api.test.activity_results_controller.sentry") as fake_sentry:
            test_obj = SimpleNamespace(id=uuid4())
            fake_test_cls.return_value = test_obj

            ctrl.create_result(payload=_payload(score=15, duration=30))

            # score < 30 → sentry.track con activity.low_score
            fake_sentry.track.assert_called_once()
            args, kwargs = fake_sentry.track.call_args
            assert args[0] == "activity.low_score"
            assert kwargs["level"] == "warning"

    def test_high_score_does_not_trigger_track(self):
        ctrl, _ = self._ctrl(patient=_patient())
        with patch("app.api.test.activity_results_controller.TestModel") as fake_test_cls, \
             patch("app.api.test.activity_results_controller.sentry") as fake_sentry:
            test_obj = SimpleNamespace(id=uuid4())
            fake_test_cls.return_value = test_obj

            ctrl.create_result(payload=_payload(score=85))

            fake_sentry.track.assert_not_called()
            # breadcrumb sí se llama siempre
            fake_sentry.breadcrumb.assert_called_once()

    def test_explicit_completed_at_preserved(self):
        ctrl, _ = self._ctrl(patient=_patient())
        explicit = datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc)
        with patch("app.api.test.activity_results_controller.TestModel") as fake_test_cls:
            test_obj = SimpleNamespace(id=uuid4())
            fake_test_cls.return_value = test_obj

            ctrl.create_result(payload=_payload(score=50, completed_at=explicit))

            kwargs = fake_test_cls.call_args.kwargs
            assert kwargs["completed_at"] == explicit
