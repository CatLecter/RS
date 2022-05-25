import sqlite3
from dataclasses import dataclass

from schemes import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


class SQLiteLoader:
    """Выгрузка данных из БД sqlite."""

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def get_table(self, table_name: str, schema: dataclass):
        """Функция получения данных из БД sqlite
        пачками по 100 записей.
        """

        table = []
        self.cursor.execute(f"""SELECT * FROM {table_name}""")
        while True:
            values = self.cursor.fetchmany(100)
            if values:
                for value in values:
                    table.append(schema(*value))
            else:
                break
        return table

    def get_all_data(self):
        """Возвращает dict с данными из БД sqlite."""

        return {
            "film_work": self.get_table("film_work", FilmWork),
            "genre": self.get_table("genre", Genre),
            "person": self.get_table("person", Person),
            "genre_film_work": self.get_table(
                "genre_film_work",
                GenreFilmWork,
            ),
            "person_film_work": self.get_table(
                "person_film_work",
                PersonFilmWork,
            ),
        }
