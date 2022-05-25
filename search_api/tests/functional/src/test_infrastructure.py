import pytest


@pytest.mark.asyncio
async def test_ping_es(create_index):
    es_ping = await create_index.ping()
    assert es_ping is True


@pytest.mark.asyncio
async def test_ping_redis(create_cache):
    redis_ping = await create_cache.ping()
    assert redis_ping == b"PONG"
