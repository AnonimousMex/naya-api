from fastapi import APIRouter, HTTPException

from app.api.games.detectiveEmociones.detective_controller import DetectiveController
from app.core.database import SessionDep


detective_router = APIRouter(prefix="/detective")

@detective_router.get("/game")
async def get_situations(session: SessionDep):
    try:
        detective_contoller = DetectiveController()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
