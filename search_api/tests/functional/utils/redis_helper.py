import pickle
from typing import Any

from aioredis import Redis


class RedisHelper:
    def __init__(self, cache: Redis):
        self.cache = cache

    async def set(self, key: str, data: Any) -> None:
        await self.cache.set(key=key, value=pickle.dumps(data))

    async def get(self, key: str) -> Any:
        data = await self.cache.get(key=key)
        if not data:
            return None
        data = pickle.loads(data)
        return data
