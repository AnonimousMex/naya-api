from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from app.api.games.game_controller import GameController
from app.api.games.game_schema import GameListResponse
from app.core.database import SessionDep
from app.core.http_response import NayaHttpResponse, NayaResponseModel


game_router = APIRouter()

@game_router.get(
        "/games",
        response_model=NayaResponseModel[list[GameListResponse]]
)
async def list_games(
    session: SessionDep,
):
    try:
        game_controller = GameController(session=session)

        games = await game_controller.get_games()
        return NayaHttpResponse.ok(data=jsonable_encoder(games))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e