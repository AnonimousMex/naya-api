from fastapi import HTTPException
from sqlmodel import Session

from app.api.games.detectiveEmociones.detective_schema import AnswerOptions, DetectiveSituationsResponse
from app.api.games.detectiveEmociones.detective_service import DetectiveService
from app.core import metrics
from app.core.http_response import NayaHttpResponse
from app.core.logger import logger


class DetectiveController:
    def __init__(self, session:Session):
        self.session = session

    async def get_situations(self):
        try:
            situations = await DetectiveService.get_situations(self.session)

            response = [
                DetectiveSituationsResponse(
                    id=sit["id"],
                    title=sit["title"],
                    story=sit["story"],
                    image=sit["image"],
                    options=[
                        AnswerOptions(id=opt["id"], name=opt["name"], isCorrect=opt["isCorrect"])
                        for opt in sit["options"]
                    ]
                )
                for sit in situations
                ]
            return response
        except HTTPException as e:
            metrics.MODULE_ERRORS.labels(module="detective").inc()
            logger.warning(
                "detective.get_situations_http_exception",
                extra={
                    "event": "detective.get_situations_http_exception",
                    "status_code": getattr(e, "status_code", None),
                    "detail": str(getattr(e, "detail", "")),
                },
            )
            NayaHttpResponse.internal_error()
        except Exception as e:
            metrics.MODULE_ERRORS.labels(module="detective").inc()
            logger.exception(
                "detective.get_situations_failed",
                extra={
                    "event": "detective.get_situations_failed",
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
            )
            NayaHttpResponse.internal_error()