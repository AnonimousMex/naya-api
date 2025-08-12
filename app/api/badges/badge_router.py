from fastapi import APIRouter, HTTPException
from app.core.database import SessionDep
from app.api.badges.badge_controller import BadgeController
from app.api.badges.badge_schema import BadgeResponseModel, UnlockBadgeRequest
from app.core.http_response import NayaHttpResponse
from fastapi.encoders import jsonable_encoder
from fastapi import Header


badge_router = APIRouter()

@badge_router.post("/unlock-badge", response_model=BadgeResponseModel)
async def unlock_badge(
    request: UnlockBadgeRequest,
    session: SessionDep,
    token: str = Header(..., alias="Authorization")
):
    try:
        badge_controller = BadgeController(session=session)

        badge = await badge_controller.unlock_badge(
            token=token,
            badge_title=request.badge_title
        )

        return NayaHttpResponse.created(
            data=jsonable_encoder(badge),
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise NayaHttpResponse.internal_error()


@badge_router.get("/badges", response_model=list[BadgeResponseModel])
async def get_badges(session: SessionDep, token: str = Header(..., alias="Authorization")):
    controller = BadgeController(session)
    return controller.get_badges(token=token)


