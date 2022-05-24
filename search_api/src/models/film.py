from enum import Enum
from typing import List, Optional

from models.general import FastJsonModel
from models.genre import GenreBrief
from models.person import PersonBrief
from pydantic import Field


class FilmFilterType(str, Enum):
    genre = "genres"
    director = "directors"
    writer = "writers"
    actor = "actors"


class FilmSortingType(str, Enum):
    imdb_rating = "imdb_rating"
    imdb_rating_desc = "-imdb_rating"


class FilmBrief(FastJsonModel):
    """Фильм (основная информация)."""

    uuid: str = Field(
        title="UUID фильма",
        example="4af6c9c9-0be0-4864-b1e9-7f87dd59ee1f",
    )
    title: str = Field(
        title="Заголовок фильма",
        max_length=255,
        example="Star Trek",
    )
    imdb_rating: Optional[float] = Field(
        title="IMDb рейтинг фильма",
        ge=0,
        le=10,
        example=7.9,
    )


class Film(FilmBrief):
    """Фильм."""

    ...
    description: Optional[str] = Field(
        title="Описание фильма",
        example="On the day of James Kirk's birth, his father dies on his damaged starship...",
    )
    genres: List[GenreBrief] = Field(
        default=[],
        title="Жанры",
        example=[
            GenreBrief(uuid="120a21cf-9097-479e-904a-13dd7198c1dd", name="Adventure"),
            GenreBrief(uuid="6c162475-c7ed-4461-9184-001ef3d9f26e", name="Sci-Fi"),
        ],
    )
    directors: List[PersonBrief] = Field(
        default=[],
        title="Режиссеры",
        example=[
            PersonBrief(
                uuid="a1758395-9578-41af-88b8-3f9456e6d938", full_name="J.J. Abrams"
            ),
        ],
    )
    writers: List[PersonBrief] = Field(
        default=[],
        title="Сценаристы",
        example=[
            PersonBrief(
                uuid="6960e2ca-889f-41f5-b728-1e7313e54d6c",
                full_name="Gene Roddenberry",
            ),
            PersonBrief(
                uuid="82b7dffe-6254-4598-b6ef-5be747193946", full_name="Alex Kurtzman"
            ),
        ],
    )
    actors: List[PersonBrief] = Field(
        default=[],
        title="Актеры",
        example=[
            PersonBrief(
                uuid="5a3d0299-2df2-4070-9fda-65ff4dfa863c", full_name="Leonard Nimoy"
            ),
            PersonBrief(
                uuid="8a34f121-7ce6-4021-b467-abec993fc6cd", full_name="Zachary Quinto"
            ),
        ],
    )
