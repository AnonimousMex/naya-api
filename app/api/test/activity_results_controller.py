"""
Controller para activity-results y métricas. Mantiene la capa HTTP delgada:
- valida el input,
- delega cálculos a MetricsService,
- registra métricas Prometheus y log estructurado.
"""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.api.emotions.emotion_model import (
    AnswerModel,
    EmotionModel,
    TestAnswerModel,
)
from app.api.test.metrics_schema import (
    ActivityResultAnswerDetail,
    ActivityResultCreate,
    ActivityResultCreated,
    ActivityResultDetail,
    ActivityResultUpdate,
    AnswerInput,
    AnswersBatchResult,
)
from app.api.test.metrics_service import MetricsService
from app.api.test.test_model import TestModel
from app.api.patients.patient_model import PatientModel
from app.constants.user_constants import CopingCategories
from app.core import metrics
from app.core import sentry_events as sentry
from app.core.http_response import NayaHttpResponse
from app.core.logger import logger


class ActivityResultsController:
    def __init__(self, session: Session):
        self.session = session

    def create_result(self, payload: ActivityResultCreate) -> ActivityResultCreated:
        """
        Crea un activity-result. Si el cliente manda `score`/`duration_seconds`,
        el resultado queda cerrado de una; si no, queda abierto y se cierra
        más tarde con PATCH. `answers` puede venir vacío (juegos rápidos).
        """
        patient = self.session.get(PatientModel, payload.child_id)
        if patient is None:
            NayaHttpResponse.not_found(data={"message": "child not found"})

        # `completed_at` solo se setea si el cliente lo manda explícito o
        # si está cerrando con score. Esto deja la opción de crear "abierto"
        # para flujos multi-paso (test estructurado).
        completed_at = payload.completed_at
        if completed_at is None and payload.score is not None:
            completed_at = datetime.now(timezone.utc)

        test = TestModel(
            user_id=patient.user_id,
            activity_id=payload.activity_id,
            score=payload.score,
            duration_seconds=payload.duration_seconds,
            completed_at=completed_at,
        )
        self.session.add(test)
        self.session.commit()
        self.session.refresh(test)

        recorded = self._insert_answers(test.id, payload.answers)
        self.session.commit()

        metrics.ACTIVITY_RESULTS.labels(role="patient").inc()
        metrics.TESTS_STARTED.inc()
        if recorded:
            metrics.TEST_ANSWERS.inc(recorded)
        if payload.score is not None:
            metrics.ACTIVITY_SCORE.observe(payload.score)
        if payload.duration_seconds is not None:
            metrics.ACTIVITY_DURATION.observe(payload.duration_seconds)
        logger.info(
            "activity_result.created",
            extra={
                "event": "activity_result.created",
                "test_id": str(test.id),
                "child_id": str(payload.child_id),
                "answers_recorded": recorded,
                "score": payload.score,
                "duration_seconds": payload.duration_seconds,
                "is_complete": completed_at is not None,
            },
        )

        # Breadcrumb (context that only surfaces if a Sentry event fires
        # later in the same request — useful for debugging without spending
        # Sentry quota).
        sentry.breadcrumb(
            category="activity",
            message="activity_result.created",
            data={
                "test_id": str(test.id),
                "child_id": str(payload.child_id),
                "answers_recorded": recorded,
                "score": payload.score,
            },
        )

        # A low score is a warning signal (UX issue or a child struggling)
        # → captured as a warning in Sentry for later analysis.
        if payload.score is not None and payload.score < 30:
            sentry.track(
                "activity.low_score",
                level="warning",
                category="business",
                tags={"event_type": "low_score"},
                extras={
                    "test_id": str(test.id),
                    "child_id": str(payload.child_id),
                    "score": payload.score,
                    "duration_seconds": payload.duration_seconds,
                },
            )

        return ActivityResultCreated(
            test_id=test.id, child_id=payload.child_id, answers_recorded=recorded
        )

    # --- ciclo de vida del activity-result ----------------------------

    def _insert_answers(
        self, test_id: UUID, answers: List[AnswerInput]
    ) -> int:
        """Inserta TestAnswerModel uno por uno, ignorando categorías inválidas.
        Instrumenta emociones detectadas y categorías de coping."""
        valid_coping = {c.value for c in CopingCategories}
        recorded = 0
        for ans in answers:
            coping = (ans.coping_category or "").strip().lower() or None
            if coping and coping not in valid_coping:
                coping = None
            self.session.add(
                TestAnswerModel(
                    test_id=test_id,
                    answer_id=ans.answer_id,
                    emotion_intensity=ans.emotion_intensity,
                    coping_category=coping,
                )
            )
            recorded += 1
            if coping:
                metrics.COPING_RECORDED.labels(category=coping).inc()
            # La emoción se infiere desde la tabla `answers` joineando
            # emotion_id. Para no hacer un query por respuesta, se carga
            # el AnswerModel y la emoción aquí — solo si la respuesta existe.
            ans_row = self.session.get(AnswerModel, ans.answer_id)
            if ans_row and ans_row.emotion_id:
                emo = self.session.get(EmotionModel, ans_row.emotion_id)
                if emo and emo.name:
                    metrics.EMOTIONS_DETECTED.labels(emotion=emo.name).inc()
        return recorded

    def add_answers(
        self, test_id: UUID, answers: List[AnswerInput]
    ) -> AnswersBatchResult:
        """Agrega respuestas a un activity-result existente. Idempotente por
        cliente (el cliente decide si reintenta enviando el mismo batch)."""
        test = self.session.get(TestModel, test_id)
        if test is None:
            NayaHttpResponse.not_found(data={"message": "activity-result not found"})

        recorded = self._insert_answers(test_id, answers)
        self.session.commit()

        total = self.session.exec(
            select(TestAnswerModel).where(TestAnswerModel.test_id == test_id)
        )
        total_count = sum(1 for _ in total)

        if recorded:
            metrics.TEST_ANSWERS.inc(recorded)
        logger.info(
            "activity_result.answers_added",
            extra={
                "event": "activity_result.answers_added",
                "test_id": str(test_id),
                "added": recorded,
                "total": total_count,
            },
        )
        return AnswersBatchResult(
            test_id=test_id, answers_recorded=recorded, total_answers=total_count
        )

    def update_result(
        self, test_id: UUID, payload: ActivityResultUpdate
    ) -> ActivityResultDetail:
        """Cierra/actualiza un activity-result. Idempotente: llamadas
        repetidas con el mismo payload producen el mismo estado."""
        test = self.session.get(TestModel, test_id)
        if test is None:
            NayaHttpResponse.not_found(data={"message": "activity-result not found"})

        changed_fields = []
        if payload.score is not None:
            test.score = payload.score
            changed_fields.append("score")
            metrics.ACTIVITY_SCORE.observe(payload.score)
        if payload.duration_seconds is not None:
            test.duration_seconds = payload.duration_seconds
            changed_fields.append("duration_seconds")
            metrics.ACTIVITY_DURATION.observe(payload.duration_seconds)
        if payload.activity_id is not None:
            test.activity_id = payload.activity_id
            changed_fields.append("activity_id")
        if payload.completed_at is not None:
            test.completed_at = payload.completed_at
            changed_fields.append("completed_at")
        elif test.completed_at is None and payload.score is not None:
            # Default razonable: si el cliente manda score y no manda
            # completed_at, asumimos que está cerrando ahora.
            test.completed_at = datetime.now(timezone.utc)
            changed_fields.append("completed_at")

        test.updated_at = datetime.now(timezone.utc)
        self.session.add(test)
        self.session.commit()
        self.session.refresh(test)

        logger.info(
            "activity_result.updated",
            extra={
                "event": "activity_result.updated",
                "test_id": str(test_id),
                "fields": changed_fields,
            },
        )
        return self.get_detail(test_id)

    def get_detail(self, test_id: UUID) -> ActivityResultDetail:
        test = self.session.get(TestModel, test_id)
        if test is None:
            NayaHttpResponse.not_found(data={"message": "activity-result not found"})

        # patient_id (child_id) desde user_id
        patient_stmt = select(PatientModel).where(PatientModel.user_id == test.user_id)
        patient = self.session.exec(patient_stmt).first()
        child_id = patient.id if patient else test.user_id

        # Respuestas con join a answers/emotions para enriquecer
        rows_stmt = (
            select(TestAnswerModel, AnswerModel, EmotionModel)
            .join(AnswerModel, AnswerModel.id == TestAnswerModel.answer_id)
            .join(EmotionModel, EmotionModel.id == AnswerModel.emotion_id, isouter=True)
            .where(TestAnswerModel.test_id == test_id)
        )
        answers: List[ActivityResultAnswerDetail] = []
        for ta, ans, emo in self.session.exec(rows_stmt):
            answers.append(
                ActivityResultAnswerDetail(
                    answer_id=ta.answer_id,
                    question_id=ans.question_id if ans else None,
                    answer_text=ans.answer_text if ans else None,
                    emotion=emo.name if emo else None,
                    emotion_intensity=ta.emotion_intensity,
                    coping_category=ta.coping_category,
                )
            )

        return ActivityResultDetail(
            test_id=test.id,
            child_id=child_id,
            activity_id=test.activity_id,
            score=test.score,
            duration_seconds=test.duration_seconds,
            created_at=test.created_at,
            completed_at=test.completed_at,
            is_complete=test.completed_at is not None,
            answers=answers,
        )

    # --- vistas para terapeuta / tutor --------------------------------

    def therapist_metrics(
        self, child_id: UUID, start, end
    ):
        metrics.METRICS_VIEW.labels(audience="therapist").inc()
        return MetricsService.therapist_metrics(
            self.session, child_id=child_id, start=start, end=end
        )

    def tutor_progress(self, child_id: UUID, start, end):
        metrics.METRICS_VIEW.labels(audience="tutor").inc()
        return MetricsService.tutor_progress(
            self.session, child_id=child_id, start=start, end=end
        )

    def activity_history(self, child_id: UUID):
        return MetricsService.activity_history(self.session, child_id=child_id)

    def recalculate(self, child_id: UUID):
        """
        Hoy las métricas se calculan on-demand a partir de tests/test_answer
        (no hay caché). Este endpoint existe como gancho idempotente: cuando
        se introduzca caché Redis, aquí se invalidará. Por ahora valida que
        el niño exista y emite un log/metric.
        """
        patient = self.session.get(PatientModel, child_id)
        if patient is None:
            NayaHttpResponse.not_found(data={"message": "child not found"})
        metrics.METRICS_RECALCULATIONS.inc()
        logger.info(
            "metrics.recalculate",
            extra={"event": "metrics.recalculate", "child_id": str(child_id)},
        )
        # Devolvemos un snapshot fresco para confirmar consistencia
        return {
            "child_id": str(child_id),
            "status": "ok",
            "note": "Métricas calculadas on-demand desde tests/test_answer. "
            "No hay caché que invalidar en esta versión.",
        }
