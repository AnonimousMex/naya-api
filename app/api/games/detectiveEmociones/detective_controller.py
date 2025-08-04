from fastapi import HTTPException
from sqlmodel import Session

from app.api.games.detectiveEmociones.detective_schema import AnswerOptions, DetectiveSituationsResponse
from app.api.games.detectiveEmociones.detective_service import DetectiveService
from app.core.http_response import NayaHttpResponse


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
                    options=[
                        AnswerOptions(id=opt["id"], name=opt["name"], isCorrect=opt["isCorrect"])
                        for opt in sit["options"]
                    ]
                )
                for sit in situations
                ]
            return response
        except HTTPException:
            NayaHttpResponse.internal_error()