import datetime
from enum import Enum
from typing import List, Optional

from models.general import FastJsonModel
from pydantic import Field


class PersonRoleType(str, Enum):
    director = "director"
    writer = "writer"
    actor = "actor"


class PersonFilm(FastJsonModel):
    """Фильм с участием персоны."""

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
    role: PersonRoleType = Field(
        title="Роль",
        max_length=25,
        example=PersonRoleType.actor,
    )


class PersonBrief(FastJsonModel):
    """Персона фильма (основная информация)."""

    uuid: str = Field(
        title="UUID персоны",
        example="5a3d0299-2df2-4070-9fda-65ff4dfa863c",
    )
    full_name: str = Field(
        title="Имя",
        max_length=255,
        example="Leonard Nimoy",
    )


class Person(PersonBrief):
    """Персона фильма."""

    ...
    birth_date: Optional[datetime.date] = Field(
        title="Дата рождения",
        example="1989-05-31",
    )
    film_works: List[PersonFilm] = Field(
        default=[],
        title="Фильмы",
        example=[
            PersonFilm(
                uuid="7b1c1238-6e7f-4e8c-8911-10a749dfb8ad",
                title="Captain Star",
                imdb_rating=7.9,
                role=PersonRoleType.actor,
            ),
            PersonFilm(
                uuid="94ca979d-8a5f-433d-93f1-076fdb838eed",
                title="Star Trek: Captain Pike",
                imdb_rating=2.4,
                role=PersonRoleType.director,
            ),
        ],
    )
