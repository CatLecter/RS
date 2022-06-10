import sys

from pydantic import BaseSettings


class Config(BaseSettings):
    broker_host: str = "rabbitmq"
    broker_port: int = 5672
    broker_user: str = "user"
    broker_password: str = "password"
    ch_host: str = "clickhouse"
    ch_port: int = 8123
    for_period: int = 14
    rs_db_host: str = "rs_db"
    rs_db_port: int = 9200


TABLES: list = ["bookmarks", "ratings", "views", "watched"]


log_config = {
    "sink": sys.stderr,
    "format": "{time} {level} {message}",
    "level": "INFO"
}

config = Config()
