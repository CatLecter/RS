import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FilmWork:
    """Датакласс, описывающий
    таблицу с фильмами.
    """

    __slots__ = (
        "id",
        "title",
        "description",
        "creation_date",
        "certificate",
        "file_path",
        "rating",
        "type",
        "created_at",
        "updated_at",
    )

    id: uuid.UUID
    title: str
    description: str
    creation_date: datetime
    certificate: datetime
    file_path: datetime
    rating: float
    type: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Genre:
    """Датакласс, описывающий
    таблицу с жанрами.
    """

    __slots__ = (
        "id",
        "name",
        "description",
        "created_at",
        "updated_at",
    )

    id: uuid.UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Person:
    """Датакласс, описывающий
    таблицу с участниками.
    """

    __slots__ = (
        "id",
        "full_name",
        "birth_date",
        "created_at",
        "updated_at",
    )

    id: uuid.UUID
    full_name: str
    birth_date: datetime
    created_at: datetime
    updated_at: datetime


@dataclass
class GenreFilmWork:
    """Датакласс, описывающий таблицу
    связи жанров и фильмов.
    """

    __slots__ = (
        "id",
        "film_work_id",
        "genre_id",
        "created_at",
    )

    id: uuid.UUID
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created_at: datetime


@dataclass
class PersonFilmWork:
    """Датакласс, описывающий таблицу
    связи участников и фильмов.
    """

    __slots__ = (
        "id",
        "film_work_id",
        "person_id",
        "role",
        "created_at",
    )

    id: uuid.UUID
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created_at: datetime
