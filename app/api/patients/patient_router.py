from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder

from app.core.database import SessionDep
from app.api.patients.patient_contoller import PatientController
from app.api.therapists.therapist_services import TherapistService
from app.api.parents.parent_controller import ParentController
from app.auth.auth_dependencies import get_current_patient_id

from .patient_schema import PatientCreateSchema, PatientResponseSchema
from app.core.http_response import NayaHttpResponse, NayaResponseModel
from app.api.parents.parent_schema import TherapistSchema


patients_router = APIRouter()

@patients_router.post(
    "/patients",
     response_model=NayaResponseModel[PatientResponseSchema],
)
async def create_patient(patient_data: PatientCreateSchema, session: SessionDep):
    try:
        patient_controller = PatientController(session=session)

        patient = await patient_controller.create_patient(patient_data=patient_data)

        return NayaHttpResponse.created(
            data=jsonable_encoder(patient),
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise e

@patients_router.get(
    "/parent/list-therapists",
    response_model=NayaResponseModel[list[TherapistSchema]],
)
async def list_verified_therapists(
    session: SessionDep,
    patient_id=Depends(get_current_patient_id),
):
    try:
        parent_controller = ParentController(session=session)
        therapists = await parent_controller.list_therapists()
        therapists_data = [therapist.model_dump() for therapist in therapists]
        return NayaHttpResponse.ok(data=therapists_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e

