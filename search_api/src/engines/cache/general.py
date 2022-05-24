from abc import ABC, abstractmethod
from typing import Any


class CacheEngine(ABC):
    """
    Абстрактный класс кэширования.
    """

    @abstractmethod
    async def save_to_cache(self, cache_key: str, data: Any) -> None:
        """Сохраняет данные в кэш."""
        pass

    @abstractmethod
    async def load_from_cache(self, cache_key: str) -> Any:
        """Загружает данные из кэша."""
        pass
