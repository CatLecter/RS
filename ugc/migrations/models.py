from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MixinModel(BaseModel):
    user_uuid: UUID
    movie_uuid: UUID
    datetime: datetime


class Bookmark(MixinModel):
    bookmarked: int


class Language(MixinModel):
    language_movie: str
    language_client: str


class Rating(MixinModel):
    rating: float


class View(MixinModel):
    progress: int


class Watched(MixinModel):
    added: int
