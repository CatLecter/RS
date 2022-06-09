from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pydantic import BaseModel


class SearchResult(BaseModel):
    """
    Ответ поискового движка.
    """

    items: List[Dict]
    total: int = 0


class SearchParams(BaseModel):
    """
    Параметры поискового запроса.
    """

    query_fields: Optional[List[str]]
    query_value: Optional[str]
    sort_field: Optional[str]
    filter_field: Optional[str]
    filter_value: Optional[str]
    page_number: int = 1
    page_size: int = 20


class SearchEngine(ABC):
    """
    Класс абстрактного поискового движка.
    """

    @abstractmethod
    async def get_by_pk(self, table: str, pk: str) -> Dict:
        """Возвращает объект по ключу."""
        pass

    @abstractmethod
    async def search(self, table: str, params: SearchParams) -> SearchResult:
        """Возвращает объекты подходящие под параметры поиска."""
        pass
