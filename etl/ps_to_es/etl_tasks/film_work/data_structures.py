import datetime
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class FilmWorkPerson:
    __slots__ = ("id", "full_name", "role")
    id: str
    full_name: str
    role: str


@dataclass(frozen=True)
class FilmWorkGenre:
    __slots__ = ("id", "name")
    id: str
    name: str


@dataclass(frozen=True)
class FilmWork:
    __slots__ = (
        "id",
        "title",
        "rating",
        "description",
        "updated_at",
        "genres",
        "persons",
    )
    id: str
    title: str
    rating: float
    description: str
    updated_at: datetime.datetime

    genres: List[FilmWorkGenre]
    persons: List[FilmWorkPerson]

    @staticmethod
    def create_from_sql_data(data: Dict) -> "FilmWork":
        genres = [
            FilmWorkGenre(*raw_genre.split("<separator>"))
            for raw_genre in data["genres"]
            if raw_genre
        ]
        persons = [
            FilmWorkPerson(*raw_person.split("<separator>"))
            for raw_person in data["persons"]
            if raw_person
        ]
        return FilmWork(
            id=data["id"],
            title=data["title"],
            rating=data["rating"],
            description=data["description"],
            updated_at=data["updated_at"],
            genres=genres,
            persons=persons,
        )

    def to_es(self):
        persons = {
            "director": [],
            "actor": [],
            "writer": [],
        }
        for person in self.persons:
            if person.role in persons.keys():
                persons[person.role].append(person)

        result = {
            "_id": self.id,
            "uuid": self.id,
            "imdb_rating": self.rating,
            "genres": [{"uuid": genre.id, "name": genre.name} for genre in self.genres],
            "title": self.title,
            "description": self.description,
            "directors_names": ",".join(
                [person.full_name for person in persons["director"]]
            ),
            "actors_names": ",".join([person.full_name for person in persons["actor"]]),
            "writers_names": ",".join(
                [person.full_name for person in persons["writer"]]
            ),
            "directors": [
                {"uuid": person.id, "full_name": person.full_name}
                for person in persons["director"]
            ],
            "actors": [
                {"uuid": person.id, "full_name": person.full_name}
                for person in persons["actor"]
            ],
            "writers": [
                {"uuid": person.id, "full_name": person.full_name}
                for person in persons["writer"]
            ],
        }
        return result
