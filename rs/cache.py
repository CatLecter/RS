from datetime import timedelta
from pickle import dumps, loads

from config import log_config
from loguru import logger
from redis import Redis, RedisError

logger.add(**log_config)


class Cache:
    def __init__(self, host: str, port: int, db: int = 0, ex: timedelta = 3600):
        self.engine = Redis(host=host, port=port, db=db)
        self.ex = ex

    def set(self, key: str, value: dict) -> None:
        _value = dumps(value)
        try:
            self.engine.set(name=key, value=_value, ex=self.ex)
        except RedisError as e:
            logger.exception(e)

    def get(self, key: str) -> dict:
        try:
            result = self.engine.get(name=key)
            return loads(result)
        except RedisError as e:
            logger.exception(e)
