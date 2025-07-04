from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from app.api.therapists.therapist_controller import TherapistController
from app.api.therapists.therapist_schema import (
    DisconnectPatientRequest,
    TherapistCreateSchema,
)
from app.core.database import SessionDep
from app.core.http_response import NayaHttpResponse, NayaResponseModel
from app.api.auth.auth_dependencies import get_current_therapist_id


therapist_router = APIRouter()


@therapist_router.post(
    "/therapist", response_model=NayaResponseModel[TherapistCreateSchema]
)
async def create_therapist(therapist_data: TherapistCreateSchema, session: SessionDep):
    try:
        therapist_controller = TherapistController(session=session)

        therapist = await therapist_controller.create_therapist(
            therapist_data=therapist_data
        )

        return NayaHttpResponse.created(
            data=jsonable_encoder(therapist),
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise e


@therapist_router.put("/disconnect-patient")
async def disconnect_patient(
    request: DisconnectPatientRequest,
    session: SessionDep,
    therapist_id: UUID = Depends(get_current_therapist_id),
):
    controller = TherapistController(session=session)
    return await controller.disconnect_patient(
        therapist_id=therapist_id,
        patient_id=request.id_patient,
    )
