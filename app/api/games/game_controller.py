from fastapi import HTTPException
from sqlmodel import Session

from app.api.games.game_service import GameService
from app.core import metrics
from app.core.http_response import NayaHttpResponse
from app.core.logger import logger


class GameController:
    def __init__(self, session: Session):
        self.session = session

    async def get_games(self):
        try:
            return await GameService.get_current_games(self.session)
        except HTTPException as e:
            metrics.MODULE_ERRORS.labels(module="games").inc()
            logger.warning(
                "games.list_http_exception",
                extra={
                    "event": "games.list_http_exception",
                    "status_code": getattr(e, "status_code", None),
                    "detail": str(getattr(e, "detail", "")),
                },
            )
            NayaHttpResponse.internal_error()
        except Exception as e:
            metrics.MODULE_ERRORS.labels(module="games").inc()
            logger.exception(
                "games.list_failed",
                extra={
                    "event": "games.list_failed",
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
            )
            NayaHttpResponse.internal_error()