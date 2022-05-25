import logging
from typing import Optional

import backoff
from core import config
from core.utils import backoff_hdlr
from elasticsearch import AsyncElasticsearch

logger = logging.getLogger(__name__)
es: Optional[AsyncElasticsearch] = None


async def get_elastic() -> AsyncElasticsearch:
    """Возвращает объект для асинхронного общения с сервисами ElasticSearch.
    Функция понадобится при внедрении зависимостей."""
    return es


@backoff.on_exception(backoff.expo, ConnectionError, on_backoff=backoff_hdlr)
async def elastic_ping():
    """Проверяет подключение к сервису ElasticSearch."""
    global es
    result = await es.ping()
    if not result:
        raise ConnectionError("The elasticsearch server is not responding.")


async def elastic_connect():
    """Устанавливает подключение к сервису ElasticSearch."""
    global es
    logger.info("Check connection to elasticsearch server.")
    es = AsyncElasticsearch(hosts=[f"{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"])
    await elastic_ping()
    logger.info("Successfully connected to elasticsearch server.")


async def elastic_disconnect():
    """Закрывает подключение к сервису ElasticSearch."""
    global es
    await es.close()
    logger.info(" Successfully disconnected from elasticsearch server.")
