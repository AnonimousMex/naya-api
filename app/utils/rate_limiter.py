from fastapi import Request
from app.core.redis import redis_client
from app.core.http_response import NayaHttpResponse
from app.constants.response_codes import NayaResponseCodes


async def rate_limiter(request: Request):
    import os
    if os.getenv("ENV") in ("development", "test"):
        return True

    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    limit = 5
    window = 60

    current_requests = await redis_client.incr(key)

    if current_requests == 1:
        await redis_client.expire(key, window)

    if current_requests > limit:
        raise NayaHttpResponse.too_many_requests(
            data=NayaResponseCodes.TOO_MANY_REQUESTS.detail,
            error_id=NayaResponseCodes.TOO_MANY_REQUESTS.code,
        )

    return True
