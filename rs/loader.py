import json
from typing import List

import backoff
from config import log_config
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ElasticsearchException
from elasticsearch.helpers import bulk
from loguru import logger
from models import PersonalRecommendation
from urllib3.exceptions import HTTPError

logger.add(**log_config)


class Loader:
    """Класс загрузки данных в Elasticsearch."""

    def __init__(self, host: str):
        self.host = host

    @backoff.on_exception(
        backoff.expo, (ElasticsearchException, HTTPError), max_tries=10
    )
    def load(self, data: List[PersonalRecommendation]) -> None:
        try:
            with Elasticsearch(hosts=self.host) as client:
                bulk(
                    client=client,
                    actions=[
                        {
                            "_index": "movies",
                            "_id": pr['user_uuid'],
                            "user_uuid": pr['user_uuid'],
                            "movies": list(pr['movies']),
                        }
                        for pr in (json.loads(data))
                    ],
                )
            logger.info("Данные загружены в Elasticsearch.")
        except ElasticsearchException as e:
            logger.exception(e)

    @backoff.on_exception(
        backoff.expo, (ElasticsearchException, HTTPError), max_tries=10
    )
    def create_index(self) -> None:
        try:
            with Elasticsearch(hosts=self.host) as client:
                with open("./indexes/movies.json", "r") as f:
                    _index = json.load(f)
                    client.indices.create(
                        index="movies",
                        body=_index,
                        ignore=400,
                    )
        except ElasticsearchException as e:
            logger.exception(e)
