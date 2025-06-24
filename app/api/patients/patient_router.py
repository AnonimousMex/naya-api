
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from app.core.database import SessionDep
from app.api.patients.patient_contoller import PatientController

from .patient_schema import PatientCreateSchema, PatientResponseSchema
from app.core.http_response import NayaHttpResponse, NayaResponseModel


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

