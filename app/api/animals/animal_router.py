from fastapi import APIRouter, HTTPException
from app.core.database import SessionDep
from app.api.animals.animal_controller import AnimalController
from .animal_schema import AnimalResponseSchema
from app.core.http_response import NayaHttpResponse, NayaResponseModel
from fastapi.encoders import jsonable_encoder

animals_router = APIRouter()

@animals_router.get(
    "/animals",
    response_model=NayaResponseModel[list[AnimalResponseSchema]],
)
async def list_animals(session: SessionDep):
    try:
        animal_controller = AnimalController(session=session)
        animals = await animal_controller.list_animals()
        return NayaHttpResponse.ok(
            data=jsonable_encoder(animals)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
