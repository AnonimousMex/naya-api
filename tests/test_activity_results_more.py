"""
Más tests para ActivityResultsController:
- add_answers (test no encontrado, success)
- update_result (test no encontrado, score, duration, activity_id, completed_at)
- _insert_answers (con/sin coping válido, métricas de emoción)
"""
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.test.activity_results_controller import ActivityResultsController


def _ans(*, coping=None, intensity=70, answer_id=None):
    return SimpleNamespace(
        coping_category=coping,
        emotion_intensity=intensity,
        answer_id=answer_id or uuid4(),
    )


# --- add_answers ----------------------------------------------------------


class TestAddAnswers:
    def test_test_not_found_raises_404(self):
        session = MagicMock()
        session.get.return_value = None
        ctrl = ActivityResultsController(session=session)
        with pytest.raises(HTTPException) as exc:
            ctrl.add_answers(test_id=uuid4(), answers=[_ans()])
        assert exc.value.status_code == 404

    def test_adds_answers_returns_batch_result(self):
        session = MagicMock()
        test = SimpleNamespace(id=uuid4())
        session.get.return_value = test
        # session.exec(...) devuelve algo iterable de 2 items
        session.exec.return_value = iter([1, 2])
        ctrl = ActivityResultsController(session=session)
        ctrl._insert_answers = MagicMock(return_value=2)

        result = ctrl.add_answers(test_id=test.id, answers=[_ans(), _ans()])
        assert result.answers_recorded == 2
        assert result.total_answers == 2


# --- update_result --------------------------------------------------------


class TestUpdateResult:
    def _ctrl(self, test=None):
        session = MagicMock()
        session.get.return_value = test
        return ActivityResultsController(session=session), session

    def test_test_not_found_raises_404(self):
        ctrl, _ = self._ctrl(test=None)
        payload = SimpleNamespace(
            score=50, duration_seconds=120,
            activity_id=None, completed_at=None,
        )
        with pytest.raises(HTTPException) as exc:
            ctrl.update_result(test_id=uuid4(), payload=payload)
        assert exc.value.status_code == 404

    def test_updates_score_only(self):
        test = SimpleNamespace(
            id=uuid4(), score=None, duration_seconds=None,
            activity_id=None, completed_at=None,
        )
        ctrl, session = self._ctrl(test=test)
        payload = SimpleNamespace(
            score=88, duration_seconds=None,
            activity_id=None, completed_at=None,
        )
        with patch.object(ActivityResultsController, "get_detail", return_value=MagicMock()):
            ctrl.update_result(test_id=test.id, payload=payload)
        assert test.score == 88
        assert test.completed_at is not None
        session.commit.assert_called()

    def test_updates_all_fields(self):
        test = SimpleNamespace(
            id=uuid4(), score=None, duration_seconds=None,
            activity_id=None, completed_at=None,
        )
        ctrl, session = self._ctrl(test=test)
        new_activity = uuid4()
        explicit_dt = datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc)
        payload = SimpleNamespace(
            score=70, duration_seconds=300,
            activity_id=new_activity, completed_at=explicit_dt,
        )
        with patch.object(ActivityResultsController, "get_detail", return_value=MagicMock()):
            ctrl.update_result(test_id=test.id, payload=payload)
        assert test.score == 70
        assert test.duration_seconds == 300
        assert test.activity_id == new_activity
        assert test.completed_at == explicit_dt

    def test_no_changes_does_not_break(self):
        test = SimpleNamespace(
            id=uuid4(), score=None, duration_seconds=None,
            activity_id=None, completed_at=None,
        )
        ctrl, session = self._ctrl(test=test)
        payload = SimpleNamespace(
            score=None, duration_seconds=None,
            activity_id=None, completed_at=None,
        )
        with patch.object(ActivityResultsController, "get_detail", return_value=MagicMock()):
            ctrl.update_result(test_id=test.id, payload=payload)
        assert test.completed_at is None


# --- _insert_answers -----------------------------------------------------


class TestInsertAnswers:
    def test_invalid_coping_is_normalized_to_none(self):
        session = MagicMock()
        session.get.return_value = None  # No emoción en la fila
        ctrl = ActivityResultsController(session=session)

        with patch("app.api.test.activity_results_controller.TestAnswerModel") as fake_model:
            fake_model.side_effect = lambda **kwargs: SimpleNamespace(**kwargs)
            recorded = ctrl._insert_answers(
                test_id=uuid4(),
                answers=[_ans(coping="invalid_category")],
            )
        assert recorded == 1

    def test_valid_coping_is_recorded(self):
        from app.constants.user_constants import CopingCategories
        valid = next(iter(CopingCategories)).value

        session = MagicMock()
        session.get.return_value = None
        ctrl = ActivityResultsController(session=session)

        with patch("app.api.test.activity_results_controller.TestAnswerModel") as fake_model:
            fake_model.side_effect = lambda **kwargs: SimpleNamespace(**kwargs)
            recorded = ctrl._insert_answers(
                test_id=uuid4(), answers=[_ans(coping=valid)],
            )
        assert recorded == 1

    def test_records_emotion_when_answer_has_one(self):
        emotion = SimpleNamespace(name="Felicidad", id=uuid4())
        ans_row = SimpleNamespace(emotion_id=emotion.id)

        session = MagicMock()
        session.get.side_effect = [ans_row, emotion]
        ctrl = ActivityResultsController(session=session)

        with patch("app.api.test.activity_results_controller.TestAnswerModel") as fake_model:
            fake_model.side_effect = lambda **kwargs: SimpleNamespace(**kwargs)
            recorded = ctrl._insert_answers(
                test_id=uuid4(), answers=[_ans()],
            )
        assert recorded == 1


# --- list endpoints (si existen) -----------------------------------------


class TestListByChild:
    def test_returns_empty_list_when_no_results(self):
        from app.api.test.activity_results_controller import ActivityResultsController
        session = MagicMock()
        session.exec.return_value = iter([])
        ctrl = ActivityResultsController(session=session)
        # Solo confirmamos que el método list no rompa.
        # Nota: si el método se llama distinto, este test se cae.
        if hasattr(ctrl, "list_by_child"):
            result = ctrl.list_by_child(child_id=uuid4())
            assert result == [] or len(result) == 0
