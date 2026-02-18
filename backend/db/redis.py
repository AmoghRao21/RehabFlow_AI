from typing import Optional

import redis.asyncio as aioredis

from core.config import get_settings
from core.logger import get_logger

logger = get_logger(__name__)

_client: Optional[aioredis.Redis] = None


async def get_redis_client() -> aioredis.Redis:
    """Return a singleton async Redis client."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )
        await _client.ping()
        logger.info("Redis client connected successfully")
    return _client


async def close_redis_client() -> None:
    """Gracefully close the Redis connection."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
        logger.info("Redis client connection closed")
