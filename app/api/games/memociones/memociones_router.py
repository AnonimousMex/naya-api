# app/api/memociones/memocion_router.py

from fastapi import APIRouter, Depends
from app.api.games.memociones.memociones_controller import MemocionController
from app.api.games.memociones.memociones_schema import MemocionPairResponse
from app.core.database import SessionDep


memociones_router = APIRouter()


@memociones_router.get("/pairs", response_model=list[MemocionPairResponse])
async def get_memorama_pairs(session: SessionDep):
    controller = MemocionController(session)
    return controller.get_memocion_pairs()
