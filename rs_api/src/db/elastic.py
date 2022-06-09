import logging
from typing import Dict, Optional

import backoff
from core import config
from core.utils import backoff_hdlr
from db.general import SearchEngine, SearchParams, SearchResult
from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch, Nested, Term

logger = logging.getLogger(__name__)
es: Optional[AsyncElasticsearch] = None


class ElasticSearchEngine(SearchEngine):
    """
    Класс поискового движка ElasticSearch.
    """

    def __init__(self, service: AsyncElasticsearch):
        self.elastic = service

    async def get_by_pk(self, table: str, pk: str) -> Optional[Dict]:
        """Возвращает объект по ключу."""
        try:
            doc = await self.elastic.get(index=table, id=pk)
        except NotFoundError:
            return None
        return doc["_source"]

    async def search(self, table: str, params: SearchParams) -> SearchResult:
        """Возвращает объекты подходящие под параметры поиска."""
        try:
            search = Search(using=self.elastic)

            # Поиск по тексту
            if params.query_fields and params.query_value:
                search = search.query(
                    MultiMatch(
                        query=params.query_value,
                        fields=params.query_fields,
                        operator="and",
                        fuzziness="AUTO",
                    )
                )

            # Сортировка
            if params.sort_field:
                search = search.sort(params.sort_field)

            # Фильтрация
            if params.filter_field:
                search = search.query(
                    Nested(
                        path=params.filter_field,
                        query=Term(
                            **{f"{params.filter_field}__uuid": params.filter_value}
                        ),
                    )
                )

            # Пагинация
            if params.page_number and params.page_size:
                start = (params.page_number - 1) * params.page_size
                end = start + params.page_size
                search = search[start:end]

            body = search.to_dict()
            docs = await self.elastic.search(index=table, body=body)
        except NotFoundError:
            return SearchResult(items=[], total=0)
        result = SearchResult(
            items=[doc["_source"] for doc in docs["hits"]["hits"]],
            total=docs["hits"]["total"]["value"],
        )
        return result


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
    print(f"{config.ELASTIC_HOST}:{config.ELASTIC_PORT}")
    es = AsyncElasticsearch(hosts=[f"{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"])
    await elastic_ping()
    logger.info("Successfully connected to elasticsearch server.")


async def elastic_disconnect():
    """Закрывает подключение к сервису ElasticSearch."""
    global es
    await es.close()
    logger.info(" Successfully disconnected from elasticsearch server.")


def get_es_search() -> AsyncElasticsearch:
    return AsyncElasticsearch(hosts=[f"{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"])
