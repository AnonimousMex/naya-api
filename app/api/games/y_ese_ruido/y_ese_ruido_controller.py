from app.api.games.y_ese_ruido.y_ese_ruido_schema import GameSoundsResponse 
from app.api.games.y_ese_ruido.y_ese_ruido_service import YEseRuidoService
from app.core.database import SessionDep


class YEseRuidoController:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_sounds(self) -> list[GameSoundsResponse]:
        return YEseRuidoService.get_sounds(self.session)

