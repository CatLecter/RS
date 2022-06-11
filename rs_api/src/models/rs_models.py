from datetime import datetime
from typing import Optional
from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class FastJsonModel(BaseModel):
    """Модель с быстрым json-сериализатором."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class MixinModel(FastJsonModel):
    uuid: UUID


class MovieBrief(MixinModel):
    """Фильм (основная информация)."""

    genres: Optional[list]


class PersonBrief(MixinModel):
    """Персона фильма (основная информация)."""

    full_name: str


class Movie(MovieBrief):
    """Фильм (подробная информация)."""

    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    directors: list[PersonBrief]
    writers: list[PersonBrief]
    actors: list[PersonBrief]


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
    movies: list[UUID]
