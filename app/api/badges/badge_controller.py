from fastapi import HTTPException
from sqlmodel import Session

from app.core.http_response import NayaHttpResponse
from app.api.badges.badge_schema import BadgeResponseModel
from app.constants.response_codes import NayaResponseCodes
from app.api.badges.badge_service import BadgeService
from app.utils.security import decode_token
from fastapi.encoders import jsonable_encoder



class BadgeController:
    def __init__(self, session: Session):
        self.session = session


    async def unlock_badge(self, token: str, badge_title: str) -> BadgeResponseModel:
        try:
            decoded = decode_token(token)
          
            if decoded:
                user_id = decoded.get("sub")
            
            if await BadgeService.badge_exists(
            self.session, user_id=user_id, badge_title=badge_title
            ):
                NayaHttpResponse.bad_request(
                data={
                    "message": NayaResponseCodes.BADGE_ALREADY_UNLOCKED.detail,
                    "providedValue": {
                        "user_id": str(user_id),
                        "badge_title": str (badge_title)
                    },
                },
                error_id=NayaResponseCodes.BADGE_ALREADY_UNLOCKED.code,
            )
            badge = await BadgeService.unlock_badge(
                self.session, user_id=user_id , badge_title=badge_title
            )
            
            badge_data = jsonable_encoder(badge)

            return BadgeResponseModel(**badge_data)

        except HTTPException as e:
            raise e

        except Exception as e:
            raise NayaHttpResponse.internal_error()
        

    def get_badges(self, token: str) -> list[BadgeResponseModel]:
        try:
            decoded = decode_token(token)
          
            if decoded:
                user_id = decoded.get("sub")
    
            return BadgeService.get_badges(self.session, user_id)
        except HTTPException as e:
            raise e

        except Exception as e:
            raise NayaHttpResponse.internal_error()