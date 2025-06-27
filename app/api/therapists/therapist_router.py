

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from app.api.therapists.therapist_controller import TherapistController
from app.api.therapists.therapist_schema import TherapistCreateSchema
from app.core.database import SessionDep
from app.core.http_response import NayaHttpResponse, NayaResponseModel


therapist_router = APIRouter()

@therapist_router.post(
    "/therapist",
    response_model=NayaResponseModel[TherapistCreateSchema]
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