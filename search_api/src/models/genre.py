from typing import Optional

from models.general import FastJsonModel
from pydantic import Field


class GenreBrief(FastJsonModel):
    """Жанр фильма (основная информация)."""

    uuid: str = Field(
        title="UUID жанра",
        example="120a21cf-9097-479e-904a-13dd7198c1dd",
    )
    name: str = Field(
        title="Название",
        max_length=255,
        example="Thriller",
    )


class Genre(GenreBrief):
    """Жанр фильма."""

    ...
    description: Optional[str] = Field(
        title="Описание жанра",
        example="Thriller is a genre of fiction, having numerous, often overlapping \
                subgenres. Thrillers are characterized...",
    )
