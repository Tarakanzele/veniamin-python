import json

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import logger

_redis: aioredis.Redis | None = None

PRICE_TTL = 310


def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def cache_price(ticker: str, price: float) -> None:
    try:
        await get_redis().setex(f"price:{ticker.upper()}", PRICE_TTL, json.dumps(price))
    except Exception as exc:
        logger.warning("Cache write failed for %s: %s", ticker, exc)


async def get_cached_price(ticker: str) -> float | None:
    try:
        value = await get_redis().get(f"price:{ticker.upper()}")
        return json.loads(value) if value else None
    except Exception as exc:
        logger.warning("Cache read failed for %s: %s", ticker, exc)
        return None
