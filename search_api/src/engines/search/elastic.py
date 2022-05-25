from typing import Dict, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch, Nested, Term
from engines.search.general import SearchEngine, SearchParams, SearchResult


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
