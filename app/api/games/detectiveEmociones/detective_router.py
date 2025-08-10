from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from app.api.games.detectiveEmociones.detective_controller import DetectiveController
from app.api.games.detectiveEmociones.detective_schema import DetectiveSituationsResponse
from app.core.database import SessionDep
from app.core.http_response import NayaHttpResponse, NayaResponseModel


detective_router = APIRouter(prefix="/detective")

@detective_router.get(
    "/game",
    response_model=NayaResponseModel[list[DetectiveSituationsResponse]]
)
async def get_situations(session: SessionDep):
    try:
        detective_contoller = DetectiveController(session=session)
        situations_game = await detective_contoller.get_situations()
        return NayaHttpResponse.ok(data=jsonable_encoder(situations_game))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
