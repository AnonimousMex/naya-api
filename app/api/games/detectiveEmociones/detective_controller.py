from fastapi import HTTPException
from sqlmodel import Session

from app.core.http_response import NayaHttpResponse


class DetectiveController:
    def __init__(self, session:Session):
        self.session = session
    
    async def get_situations(self):
        try:
            await DetectiveController.get_situations(self.session)
        except HTTPException:
            NayaHttpResponse.internal_error()