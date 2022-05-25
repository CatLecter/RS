import logging
import pickle
from datetime import timedelta
from typing import Any

from aioredis import Redis
from engines.cache.general import CacheEngine

logger = logging.getLogger(__name__)


class RedisCacheEngine(CacheEngine):
    """
    Реализация кеширования на основе сервиса Redis.
    """

    def __init__(self, redis: Redis, ttl: timedelta = 60):
        self.redis = redis
        self.expire = int(ttl.total_seconds())

    async def save_to_cache(self, cache_key: str, data: Any) -> None:
        """Сохраняет данные в кэш."""
        logger.info(f'Put data to Redis by key "{cache_key}".')
        await self.redis.set(
            key=cache_key,
            value=pickle.dumps(data),
            expire=self.expire,
        )

    async def load_from_cache(self, cache_key: str) -> Any:
        """Загружает данные из кэша."""
        logger.info(f'Get data from Redis by key "{cache_key}".')
        data = await self.redis.get(key=cache_key)
        if not data:
            return None
        data = pickle.loads(data)
        return data
