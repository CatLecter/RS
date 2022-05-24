import json
from dataclasses import dataclass

import aiofiles as aiofiles
import aiohttp
import aioredis
import pytest
from multidict import CIMultiDictProxy
from tests.functional.settings import config
from tests.functional.utils.es_helper import ESHelper


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope="module")
def event_loop():
    """Решение проблемы с фикстурами: Event loop is closed."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def create_index():
    """Создаёт индексы перед сессией тестов и
    удаляет их после окончания тестов.
    """

    es_helper = ESHelper()
    await es_helper.create_index()
    await es_helper.load_data()
    if await es_helper.check_data_in_index():
        yield es_helper.client
    await es_helper.delete_index()
    await es_helper.client.close()


@pytest.fixture(scope="session")
async def create_cache():
    """Создаёт объект кэша и очищает его перед работой и после."""

    redis = await aioredis.create_redis_pool((config.REDIS_HOST, config.REDIS_PORT))
    await redis.flushall()
    yield redis
    await redis.flushall()
    redis.close()
    await redis.wait_closed()


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        url = f"http://{config.SERVICE_URL}:{config.SERVICE_PORT}/api/v1{method}"
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture
def test_data():
    async def inner(name_index: str):
        file = config.data_dir.joinpath(f"{name_index}.json")
        async with aiofiles.open(file, encoding="utf-8") as f:
            content = await f.read()
            response = json.loads(content)
        return response

    return inner
