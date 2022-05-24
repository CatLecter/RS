import json
from typing import Dict, List, Tuple

import backoff
import elasticsearch
from elasticsearch import Elasticsearch, helpers
from log_utils import get_logger
from settings.settings import get_settings

settings = get_settings()
logger = get_logger(__name__)


def backoff_hdlr(details):
    logger.error(
        "Взяли паузу {wait:0.1f} секунд после {tries} попыток "
        "вызова функции {target} с аргументами {args} и позиционными аргументами "
        "{kwargs}".format(**details)
    )


@backoff.on_exception(
    backoff.expo, elasticsearch.exceptions.ConnectionError, on_backoff=backoff_hdlr
)
def get_connection() -> Elasticsearch:
    """Организует подключение к Elasticsearch."""
    try:
        logger.debug("Подключение к базе данных Elasticsearch...")
        conf = {
            "host": settings.elastic.host,
        }
        connection = Elasticsearch([conf])
        logger.debug("Успех!")
        return connection
    except Exception as e:
        logger.error(e)
        raise e


class ES:
    """
    Вспомогательный класс для работы с Elasticsearch.
    """

    def __init__(self):
        self._es = get_connection()

    @backoff.on_exception(
        backoff.expo, elasticsearch.exceptions.ConnectionError, on_backoff=backoff_hdlr
    )
    def is_index_exist(self, index_name: str) -> bool:
        """Проверяет существование индекса в базе."""
        return self._es.indices.exists(index=index_name)

    @backoff.on_exception(
        backoff.expo, elasticsearch.exceptions.ConnectionError, on_backoff=backoff_hdlr
    )
    def create_index(
        self, index_name: str, index_mapping: Dict, index_settings: Dict = None
    ) -> Dict:
        """Создает индекс в базе."""
        result = self._es.indices.create(
            index=index_name,
            mappings=index_mapping,
            settings=index_settings,
            ignore=400,  # Игнорирование кода 400 - Индекс уже существует
        )
        logger.info(
            f'Результат создания индекса "{index_name}":\n'
            f"{json.dumps(result, indent=2)}"
        )
        return result

    @backoff.on_exception(
        backoff.expo, elasticsearch.exceptions.ConnectionError, on_backoff=backoff_hdlr
    )
    def insert_chunk(self, chunk: List[Dict], es_index: str) -> Tuple[int, List]:
        return helpers.bulk(self._es, chunk, index=es_index)


def get_es_instance() -> ES:
    return ES()
