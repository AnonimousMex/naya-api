from app.api.games.memociones.memociones_schema import MemocionPairResponse
from app.api.games.memociones.memociones_service import MemocionService
from app.core.database import SessionDep


class MemocionController:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_memocion_pairs(self) -> list[MemocionPairResponse]:
        return MemocionService.get_emotion_situation_pairs(self.session)
