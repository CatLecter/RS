from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

import orjson
from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class FastJsonModel(BaseModel):
    """Модель с быстрым json-сериализатором."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class MixinModel(BaseModel):
    uuid: UUID


class MovieBrief(MixinModel):
    """Фильм (основная информация)."""

    genres: Optional[list]


class PersonBrief(MixinModel):
    """Персона фильма (основная информация)."""

    full_name: str


class Movie(FastJsonModel):
    """Фильм (подробная информация)."""

    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    directors: List[PersonBrief]
    writers: List[PersonBrief]
    actors: List[PersonBrief]


class MixinEvent(BaseModel):
    user_uuid: UUID
    movie: Optional[MovieBrief]
    datetime: datetime


class RatingEvent(MixinEvent):
    rating: int


class BookmarkEvent(MixinEvent):
    bookmarked: Optional[bool]


class ViewEvent(MixinEvent):
    progress: Optional[int]


class WatchEvent(MixinEvent):
    added: Optional[bool]


class PersonalRecommendation(BaseModel):
    """Список фильмов подобранных для
    пользователя рекомендательной системой
    """

    user_uuid: UUID
    movies: List[UUID]
