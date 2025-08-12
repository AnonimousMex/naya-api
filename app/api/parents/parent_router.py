from fastapi import APIRouter, Depends
from app.core.database import SessionDep
from app.core.http_response import NayaHttpResponse, NayaResponseModel
from app.api.auth.auth_dependencies import get_current_patient_id
from app.api.parents.parent_controller import ParentController
from app.api.parents.parent_schema import TherapistSchema
from typing import List

parent_router = APIRouter()

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
        return NayaHttpResponse.error(
            status=500,
            status_message=f"Error interno del servidor: {str(e)}"
        )
