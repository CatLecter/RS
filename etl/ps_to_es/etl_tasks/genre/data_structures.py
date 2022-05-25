import datetime
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Genre:
    __slots__ = ("id", "name", "description", "updated_at")
    id: str
    name: str
    description: str
    updated_at: datetime.datetime

    @staticmethod
    def create_from_sql_data(data: Dict) -> "Genre":
        return Genre(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            updated_at=data["updated_at"],
        )

    def to_es(self):
        result = {
            "_id": self.id,
            "uuid": self.id,
            "name": self.name,
            "description": self.description,
        }
        return result
