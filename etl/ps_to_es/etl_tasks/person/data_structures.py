import datetime
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class PersonFilmWork:
    __slots__ = ("id", "title", "rating", "role")
    id: str
    title: str
    rating: float
    role: str


@dataclass(frozen=True)
class Person:
    __slots__ = ("id", "full_name", "birth_date", "role", "updated_at", "film_works")
    id: str
    full_name: str
    birth_date: datetime.date
    updated_at: datetime.datetime

    film_works: List[PersonFilmWork]

    @staticmethod
    def create_from_sql_data(data: Dict) -> "Person":
        film_works = [
            PersonFilmWork(*film_work.split("<separator>"))
            for film_work in data["film_works"]
            if film_work
        ]
        return Person(
            id=data["id"],
            full_name=data["full_name"],
            birth_date=data["birth_date"],
            updated_at=data["updated_at"],
            film_works=film_works,
        )

    def to_es(self):
        result = {
            "_id": self.id,
            "uuid": self.id,
            "full_name": self.full_name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "film_works": [
                {
                    "uuid": film_work.id,
                    "title": film_work.title,
                    "imdb_rating": film_work.rating,
                    "role": film_work.role,
                }
                for film_work in self.film_works
            ],
        }
        return result
