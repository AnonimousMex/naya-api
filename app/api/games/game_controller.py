from fastapi import HTTPException
from sqlmodel import Session

from app.api.games.game_service import GameService
from app.core.http_response import NayaHttpResponse


class GameController:
    def __init__(self, session: Session):
        self.session = session
    
    async def get_games(self):
        try:
            return await GameService.get_current_games(self.session)
        except HTTPException:
            NayaHttpResponse.internal_error()