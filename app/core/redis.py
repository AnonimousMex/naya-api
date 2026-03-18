import redis.asyncio as redis
from app.core.settings import settings

redis_client = redis.from_url(
    "redis://redis:6379", encoding="utf-8", decode_responses=True
)
