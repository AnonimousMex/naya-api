"""
Endpoints para activity-results y métricas diferenciadas terapeuta/tutor.

Ciclo de vida del recurso `activity-result`:
- POST   /activity-results                          → crea (con o sin answers)
- POST   /activity-results/{test_id}/answers        → agrega respuestas
- PATCH  /activity-results/{test_id}                → cierra/actualiza
- GET    /activity-results/{test_id}                → detalle

Vistas agregadas:
- GET    /therapist/children/{child_id}/metrics
- GET    /tutor/children/{child_id}/progress
- GET    /children/{child_id}/activity-history
- POST   /children/{child_id}/recalculate-metrics
"""
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.auth.role_dependencies import (
    assert_can_view_child_history,
    assert_therapist_can_view_child,
    assert_tutor_can_view_child,
)
from app.api.test.activity_results_controller import ActivityResultsController
from app.api.test.metrics_schema import (
    ActivityResultCreate,
    ActivityResultCreated,
    ActivityResultDetail,
    ActivityResultUpdate,
    AnswersBatch,
    AnswersBatchResult,
    TherapistMetricsResponse,
    TutorProgressResponse,
)
from app.core.database import SessionDep
from app.core.http_response import NayaHttpResponse, NayaResponseModel

activity_results_router = APIRouter()


@activity_results_router.post(
    "/activity-results",
    response_model=NayaResponseModel[ActivityResultCreated],
)
def register_activity_result(payload: ActivityResultCreate, session: SessionDep):
    controller = ActivityResultsController(session=session)
    data = controller.create_result(payload)
    return NayaHttpResponse.ok(data=data.model_dump(mode="json"))


@activity_results_router.post(
    "/activity-results/{test_id}/answers",
    response_model=NayaResponseModel[AnswersBatchResult],
)
def add_activity_result_answers(
    test_id: UUID, payload: AnswersBatch, session: SessionDep
):
    """Agrega respuestas a un activity-result existente. Llamable múltiples
    veces (cada llamada agrega; el cliente decide si reintenta)."""
    controller = ActivityResultsController(session=session)
    data = controller.add_answers(test_id, payload.answers)
    return NayaHttpResponse.ok(data=data.model_dump(mode="json"))


@activity_results_router.patch(
    "/activity-results/{test_id}",
    response_model=NayaResponseModel[ActivityResultDetail],
)
def update_activity_result(
    test_id: UUID, payload: ActivityResultUpdate, session: SessionDep
):
    """Cierra/actualiza un activity-result. Idempotente."""
    controller = ActivityResultsController(session=session)
    data = controller.update_result(test_id, payload)
    return NayaHttpResponse.ok(data=data.model_dump(mode="json"))


@activity_results_router.get(
    "/activity-results/{test_id}",
    response_model=NayaResponseModel[ActivityResultDetail],
)
def get_activity_result(test_id: UUID, session: SessionDep):
    """Detalle de un activity-result (útil para reanudar/auditar)."""
    controller = ActivityResultsController(session=session)
    data = controller.get_detail(test_id)
    return NayaHttpResponse.ok(data=data.model_dump(mode="json"))


@activity_results_router.get(
    "/therapist/children/{child_id}/metrics",
    response_model=NayaResponseModel[TherapistMetricsResponse],
)
def therapist_metrics(
    child_id: UUID,
    session: SessionDep,
    start: Optional[date] = Query(default=None),
    end: Optional[date] = Query(default=None),
    _claims=Depends(assert_therapist_can_view_child),
):
    controller = ActivityResultsController(session=session)
    return NayaHttpResponse.ok(
        data=controller.therapist_metrics(child_id, start, end)
    )


@activity_results_router.get(
    "/tutor/children/{child_id}/progress",
    response_model=NayaResponseModel[TutorProgressResponse],
)
def tutor_progress(
    child_id: UUID,
    session: SessionDep,
    start: Optional[date] = Query(default=None),
    end: Optional[date] = Query(default=None),
    _claims=Depends(assert_tutor_can_view_child),
):
    controller = ActivityResultsController(session=session)
    return NayaHttpResponse.ok(data=controller.tutor_progress(child_id, start, end))


@activity_results_router.get(
    "/children/{child_id}/activity-history",
)
def activity_history(
    child_id: UUID,
    session: SessionDep,
    _claims=Depends(assert_can_view_child_history),
):
    controller = ActivityResultsController(session=session)
    return NayaHttpResponse.ok(data=controller.activity_history(child_id))


@activity_results_router.post(
    "/children/{child_id}/recalculate-metrics",
)
def recalculate(
    child_id: UUID,
    session: SessionDep,
    _claims=Depends(assert_therapist_can_view_child),
):
    """Solo terapeutas pueden forzar recálculo (operación administrativa)."""
    controller = ActivityResultsController(session=session)
    return NayaHttpResponse.ok(data=controller.recalculate(child_id))
