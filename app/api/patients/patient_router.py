from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder

from app.core.database import SessionDep
from app.api.patients.patient_contoller import PatientController
from app.api.therapists.therapist_services import TherapistService
from app.api.auth.auth_dependencies import get_current_patient_id

from .patient_schema import PatientCreateSchema, PatientResponseSchema
from app.core.http_response import NayaHttpResponse, NayaResponseModel
from app.api.therapists.therapist_schema import TherapistListResponseSchema


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
    response_model=NayaResponseModel[list[TherapistListResponseSchema]],
)
async def list_verified_therapists(
    session: SessionDep,
    patient_id=Depends(get_current_patient_id),
):
    try:
        therapists = await TherapistService.list_verified_therapists(session)
        return NayaHttpResponse.ok(data=jsonable_encoder(therapists))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e

