from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.auth.auth_dependencies import get_current_patient_id
from app.api.auth.role_dependencies import assert_current_parent
from app.api.parents.parent_controller import ParentController
from app.api.parents.parent_schema import ChildSchema, TherapistSchema
from app.core import metrics
from app.core.database import SessionDep
from app.core.http_response import NayaHttpResponse, NayaResponseModel
from app.core.logger import logger

parent_router = APIRouter()


@parent_router.get(
    "/parent/children",
    response_model=NayaResponseModel[List[ChildSchema]],
)
def list_children(
    session: SessionDep,
    claims: Dict[str, Any] = Depends(assert_current_parent),
):
    """
    Lista los niños vinculados al tutor (PARENT) autenticado.
    Solo accesible si el rol del token es PARENT.
    """
    parent_controller = ParentController(session=session)
    children = parent_controller.list_children(UUID(claims["user_id"]))
    metrics.METRICS_VIEW.labels(audience="tutor_list_children").inc()
    return NayaHttpResponse.ok(
        data=[c.model_dump(mode="json") for c in children]
    )

@parent_router.get(
    "/parent/list-therapists", 
    response_model=NayaResponseModel[List[TherapistSchema]]
)
async def list_therapists(
    session: SessionDep,
    current_patient_id: str = Depends(get_current_patient_id)
):
    """
    Lista todos los terapeutas disponibles con información completa para mostrar en el CV
    """
    try:
        parent_controller = ParentController(session=session)
        therapists = await parent_controller.list_therapists()

        return NayaHttpResponse.success(
            data=therapists,  # Devolver directamente la lista de terapeutas
            status=200,
            status_message="Terapeutas obtenidos exitosamente"
        )
    except Exception as e:
        metrics.MODULE_ERRORS.labels(module="parents").inc()
        logger.exception(
            "parent.list_therapists_failed",
            extra={
                "event": "parent.list_therapists_failed",
                "error_class": e.__class__.__name__,
                "error": str(e),
            },
        )
        return NayaHttpResponse.error(
            status=500,
            status_message=f"Error interno del servidor: {str(e)}"
        )
