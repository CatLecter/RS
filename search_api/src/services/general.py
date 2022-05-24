from abc import ABCMeta, abstractmethod
from typing import Optional, TypeVar

from engines.cache.general import CacheEngine
from engines.search.general import SearchEngine, SearchParams
from models.general import Page

ST = TypeVar("ST")
FT = TypeVar("FT")


class GeneralService(metaclass=ABCMeta):
    def __init__(self, cache_engine: CacheEngine, search_engine: SearchEngine):
        self.cache_engine = cache_engine
        self.search_engine = search_engine

    @property
    @abstractmethod
    def table(self):
        """Индекс или таблица в поисковом движке."""
        pass

    @property
    @abstractmethod
    def query_fields(self):
        """Поля по которым может производиться поиск."""
        pass

    @property
    @abstractmethod
    def item_dataclass(self):
        """Класс на который будут мапиться выходные данные."""
        pass

    @property
    @abstractmethod
    def item_brief_dataclass(self):
        """Класс на который будут мапиться выходные данные, если они должны быть выведены в краткой форме."""
        pass

    async def get_by_uuid(self, uuid: str) -> Optional[FT]:
        """Возвращает объект по UUID."""
        cache_key = f"{self.table}:get_by_uuid(uuid={uuid})"

        data = await self.cache_engine.load_from_cache(cache_key)
        if not data:
            data = await self.search_engine.get_by_pk(table=self.table, pk=uuid)
            if not data:
                return None
            await self.cache_engine.save_to_cache(cache_key, data)

        return self.item_dataclass(**data)

    async def search(self, query: str, page_number: int, page_size: int) -> Page[ST]:
        """Ищет объекты по поисковым полям. Не кеширует результаты, так как вариантов может быть очень много."""
        params = SearchParams(
            query_fields=self.query_fields,
            query_value=query,
            page_number=page_number,
            page_size=page_size,
        )

        search_results = await self.search_engine.search(
            table=self.table, params=params
        )

        data_page = Page(
            items=[self.item_brief_dataclass(**item) for item in search_results.items],
            total=search_results.total,
            page_number=page_number,
            page_size=page_size,
        )
        return data_page
