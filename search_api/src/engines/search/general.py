from abc import ABC, abstractmethod

from pydantic import BaseModel


class SearchResult(BaseModel):
    """
    Ответ поискового движка.
    """

    items: list[dict]
    total: int = 0


class SearchParams(BaseModel):
    """
    Параметры поискового запроса.
    """

    query_fields: list[str] | None
    query_value: str | None
    sort_field: str | None
    filter_field: str | None
    filter_value: str | None
    page_number: int = 1
    page_size: int = 20


class SearchEngine(ABC):
    """
    Класс абстрактного поискового движка.
    """

    @abstractmethod
    async def get_by_pk(self, table: str, pk: str) -> dict:
        """Возвращает объект по ключу."""
        pass

    @abstractmethod
    async def search(self, table: str, params: SearchParams) -> SearchResult:
        """Возвращает объекты подходящие под параметры поиска."""
        pass
