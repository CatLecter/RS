from typing import Generic, List, Optional, TypeVar

import orjson
from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class FastJsonModel(BaseModel):
    """Модель с быстрым json-сериализатором."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


PT = TypeVar("PT")


class Page(FastJsonModel, Generic[PT]):
    """Страница результатов с пагинацией."""

    items: List[PT] = Field(
        default=[],
        title="Список объектов",
    )

    total: Optional[int] = Field(
        title="Всего объектов",
        example=35,
    )
    page_number: Optional[int] = Field(
        title="Номер страницы",
        example=1,
    )
    page_size: Optional[int] = Field(
        title="Объектов на странице",
        example=20,
    )
