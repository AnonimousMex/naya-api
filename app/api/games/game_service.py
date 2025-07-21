from sqlmodel import select
from app.api.games.game_schema import GameListResponse
from app.models.game_model import GameModel


class GameService:
    @staticmethod
    async def get_current_games(
        session
    )-> list[GameModel]:
        result = session.exec(select(GameModel)).all()
        games = [
            GameListResponse(
                id=game.id,
                name=game.name,
                description=game.description,
                image_url=game.image_url,
            )
            for game in result
        ]
        return games