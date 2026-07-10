import json

# redis.asyncio — асинхронный клиент Redis для использования с asyncio
import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import logger

# Глобальная переменная для хранения единственного соединения с Redis
_redis: aioredis.Redis | None = None

# Время жизни кеша в секундах — чуть больше интервала обновления (300с),
# чтобы цена не пропала из кеша между двумя запусками задачи
PRICE_TTL = 310


def get_redis() -> aioredis.Redis:
    global _redis
    # Создаём соединение один раз (паттерн Singleton)
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def cache_price(ticker: str, price: float) -> None:
    try:
        # setex: SET + EX (expiry) — ключ автоматически удалится через PRICE_TTL секунд
        # json.dumps превращает float в строку для хранения в Redis
        await get_redis().setex(f"price:{ticker.upper()}", PRICE_TTL, json.dumps(price))
    except Exception as exc:
        # Ошибка кеша не должна ломать основной процесс — только логируем
        logger.warning("Cache write failed for %s: %s", ticker, exc)


async def get_cached_price(ticker: str) -> float | None:
    try:
        # Читаем значение из Redis по ключу
        value = await get_redis().get(f"price:{ticker.upper()}")
        # None если ключ не найден (TTL истёк или цена ещё не кешировалась)
        return json.loads(value) if value else None
    except Exception as exc:
        logger.warning("Cache read failed for %s: %s", ticker, exc)
        return None
