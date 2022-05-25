from typing import Any

from engines.cache.general import CacheEngine


class DummyCacheEngine(CacheEngine):
    """
    Класс заглушка не осуществляющий реального кэширования.
    """

    async def save_to_cache(self, cache_key: str, data: Any) -> None:
        pass

    async def load_from_cache(self, cache_key: str) -> Any:
        return None
