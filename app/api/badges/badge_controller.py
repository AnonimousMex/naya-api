from fastapi import HTTPException
from sqlmodel import Session

from app.core import metrics
from app.core.http_response import NayaHttpResponse
from app.core.logger import logger
from app.api.badges.badge_schema import BadgeResponseModel
from app.constants.response_codes import NayaResponseCodes
from app.api.badges.badge_service import BadgeService
from app.utils.security import decode_token, get_user_id_from_token
from fastapi.encoders import jsonable_encoder



class BadgeController:
    def __init__(self, session: Session):
        self.session = session


    async def unlock_badge(self, token: str, badge_title: str) -> BadgeResponseModel:
        try:
            user_id = get_user_id_from_token(token)
            if await BadgeService.badge_exists(
            self.session, user_id=user_id, badge_title=badge_title
            ):
                logger.info(
                    "badge.already_unlocked",
                    extra={
                        "event": "badge.already_unlocked",
                        "user_id": str(user_id),
                        "badge_title": badge_title,
                    },
                )
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
            logger.info(
                "badge.unlocked",
                extra={
                    "event": "badge.unlocked",
                    "user_id": str(user_id),
                    "badge_title": badge_title,
                },
            )
            return BadgeResponseModel(**badge_data)

        except HTTPException as e:
            raise e

        except Exception as e:
            metrics.MODULE_ERRORS.labels(module="badges").inc()
            logger.exception(
                "badge.unlock_failed",
                extra={
                    "event": "badge.unlock_failed",
                    "badge_title": badge_title,
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
            )
            raise NayaHttpResponse.internal_error()


    def get_badges(self, token: str) -> list[BadgeResponseModel]:
        try:
            user_id = get_user_id_from_token(token)
            return BadgeService.get_badges(self.session, user_id)
        except HTTPException as e:
            raise e

        except Exception as e:
            metrics.MODULE_ERRORS.labels(module="badges").inc()
            logger.exception(
                "badge.list_failed",
                extra={
                    "event": "badge.list_failed",
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
            )
            raise NayaHttpResponse.internal_error()