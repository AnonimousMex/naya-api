from fastapi import APIRouter
from app.api.games.y_ese_ruido.y_ese_ruido_schema import GameSoundsResponse
from app.api.games.y_ese_ruido.y_ese_ruido_controller import YEseRuidoController 
from app.core.database import SessionDep


y_ese_ruido_router = APIRouter()


@y_ese_ruido_router.get("/sounds", response_model=list[GameSoundsResponse])
async def get_sounds(session: SessionDep):
    controller = YEseRuidoController(session)
    return controller.get_sounds()
