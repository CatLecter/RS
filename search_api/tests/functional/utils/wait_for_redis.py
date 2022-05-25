import asyncio
import os

import aioredis
import backoff
from logger import get_logger

logger = get_logger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))


@backoff.on_exception(backoff.expo, ConnectionError, max_time=30)
async def redis_ping(redis):
    """Проверяет подключение к сервису Redis."""
    ping = await redis.ping()
    if ping != b"PONG":
        raise ConnectionError("WAIT_FOR_REDIS: The redis server is not responding.")
    logger.info("WAIT_FOR_REDIS: Successfully connected to redis server.")


async def main():
    logger.info("WAIT_FOR_REDIS: Check connection to redis server.")
    redis = await aioredis.create_redis_pool(
        (REDIS_HOST, REDIS_PORT), minsize=10, maxsize=20
    )
    await redis_ping(redis)
    redis.close()
    await redis.wait_closed()
    logger.info("WAIT_FOR_REDIS: Successfully disconnected from redis server.")


if __name__ == "__main__":
    asyncio.run(main())
