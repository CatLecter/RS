import datetime
from dataclasses import dataclass
from typing import Iterator, List, Type, TypeVar

import backoff
import psycopg2
from log_utils import get_logger
from psycopg2.extensions import connection as pg_connection
from psycopg2.extras import RealDictCursor
from settings.settings import get_settings

settings = get_settings()
logger = get_logger(__name__)

DT = TypeVar("DT")


@dataclass(frozen=True)
class DBItem:
    __slots__ = ("id", "updated_at")
    id: str
    updated_at: datetime.datetime


def backoff_hdlr(details):
    logger.error(
        "Взяли паузу {wait:0.1f} секунд после {tries} попыток "
        "вызова функции {target} с аргументами {args} и позиционными аргументами "
        "{kwargs}".format(**details)
    )


@backoff.on_exception(backoff.expo, psycopg2.DatabaseError, on_backoff=backoff_hdlr)
def get_connection() -> pg_connection:
    """Организует подключение к PostgreSQL."""
    try:
        logger.debug("Подключение к базе данных PostgreSQL...")
        connection = psycopg2.connect(**settings.postgress_dsn.dict())
        logger.debug("Успех!")
        return connection
    except (Exception, psycopg2.DatabaseError) as e:
        logger.error(f"ОШИБКА: {e}")
        raise e


class PGFilmWorkExtractor:
    """
    Класс для извлечения записей из Postgres необходимых для переноса в Elasticsearch.
    """

    def __init__(self):
        self.connection = get_connection()
        self.cursor = self.connection.cursor()

    @backoff.on_exception(backoff.expo, psycopg2.DatabaseError, on_backoff=backoff_hdlr)
    def create_iterator(
        self, query: str, last_updated: str, chunk_size: int
    ) -> Iterator[List[DBItem]]:
        """
        Возвращает данные из базы по частям заданной длинны.

        Yields:
            list of dataclass: Список записей таблицы.
        """
        try:
            self.cursor.execute(query, (last_updated,))
            while results := self.cursor.fetchmany(chunk_size):
                data = list([DBItem(*result) for result in results])
                yield data

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"ОШИБКА: {error}")
            raise error


class PGFilmWorkEnricher:
    """
    Класс для обогащения записей из Postgres необходимыми данными для переноса в Elasticsearch.
    """

    def __init__(self):
        self.connection = get_connection()
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)

    @backoff.on_exception(backoff.expo, psycopg2.DatabaseError, on_backoff=backoff_hdlr)
    def get_enriched_data_chunk(
        self, query: str, data_chunk: List[DBItem], data_class: Type[DT]
    ) -> List[DT]:
        """Возвращает насыщенные данные."""
        item_ids = [data.id for data in data_chunk]
        query = self.cursor.mogrify(query, (item_ids,))
        self.cursor.execute(query)
        db_data = self.cursor.fetchall()
        enriched_data_chunk = [
            data_class.create_from_sql_data(data) for data in db_data
        ]
        return enriched_data_chunk
