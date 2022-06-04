from pydantic import BaseSettings


class Config(BaseSettings):
    broker_host: str = "rabbitmq"
    broker_port: int = 5672
    broker_user: str = "user"
    broker_password: str = "password"
    ch_host: str = "clickhouse"
    ch_port: int = 8123
    for_period: int = 14


TABLES: list = ["bookmarks", "language", "ratings", "views", "watched"]


log_config = {
    "sink": "./log/rs.log",
    "format": "{time} {level} {message}",
    "level": "INFO",
    "rotation": "00:00",
    "compression": "zip",
}

config = Config()
