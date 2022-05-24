import json

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from tests.functional.settings import config
from tests.functional.utils.utils import names_file


class ESHelper:
    def __init__(self) -> None:
        self.client = AsyncElasticsearch(
            hosts=f"{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"
        )

    async def create_index(self):
        """Метод создаёт индексы, лежащие в папке testdata/indexes.
        Наименование индекса в Elasticsearch совпадает с именем файла.
        """

        for name in names_file(config.indexes_dir):
            with open(
                config.indexes_dir.joinpath(f"{name}.json"), "r", encoding="utf-8"
            ) as f:
                index_data = json.load(f)
            await self.client.indices.create(index=name, body=index_data, ignore=400)

    async def load_data(self):
        """Метод загружает данные лежащие в папке
        testdata/data_for_indexes в индексы.
        Имена файлов должны соответствовать имени индекса.
        """

        for name in names_file(config.data_dir):
            with open(
                config.data_dir.joinpath(f"{name}.json"), "r", encoding="utf-8"
            ) as f:
                index_data = json.load(f)
            await async_bulk(
                client=self.client,
                actions=[
                    {"_index": name, "_id": essence["uuid"], **essence}
                    for essence in index_data
                ],
            )

    async def check_data_in_index(self):
        for name in names_file(config.indexes_dir):
            items = {}
            while not items.get("count"):
                items = await self.client.count(index=name)
        return True

    async def delete_index(self):
        """Метод удаляет индексы по их названию."""

        for name in names_file(config.indexes_dir):
            await self.client.indices.delete(index=name, ignore=[400, 404])
