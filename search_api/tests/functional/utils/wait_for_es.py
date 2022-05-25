import asyncio
import os

import backoff
from elasticsearch import AsyncElasticsearch
from logger import get_logger

logger = get_logger(__name__)

ELASTIC_HOST = os.getenv("ELASTIC_HOST", "elastic")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))


@backoff.on_exception(backoff.expo, ConnectionError, max_time=30)
async def elastic_ping(es):
    """Проверяет подключение к сервису ElasticSearch."""
    result = await es.ping()
    if not result:
        raise ConnectionError(
            "WAIT_FOR_ES: The elasticsearch server is not responding."
        )


async def main():
    logger.info("WAIT_FOR_ES: Check connection to elasticsearch server.")
    es = AsyncElasticsearch(hosts=[f"{ELASTIC_HOST}:{ELASTIC_PORT}"])
    await elastic_ping(es)
    logger.info("WAIT_FOR_ES: Successfully connected to elasticsearch server.")
    await es.close()
    logger.info("WAIT_FOR_ES: Successfully disconnected from elasticsearch server.")


if __name__ == "__main__":
    asyncio.run(main())
