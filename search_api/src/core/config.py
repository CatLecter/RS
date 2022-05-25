import os
from datetime import timedelta
from logging import config as logging_config

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Настройки проекта.
PROJECT_NAME = "Фильмотека"
PROJECT_DESCRIPTION = "База данных фильмов."
PROJECT_VERSION = "1.0"
PROJECT_LICENSE_INFO = {
    "name": "Apache 2.0",
    "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
}
PROJECT_TAGS_METADATA = [
    {
        "name": "Фильмы",
        "description": "**Поиск**, **сортировка**, **фильтрация** и **детальная \
        информация** о фильмах в фильмотеке.",
    },
    {
        "name": "Персоны",
        "description": "**Поиск** и **детальная информация** об актерах, сценаристах и \
        режиссерах фильмотеки.",
    },
    {
        "name": "Жанры",
        "description": "**Список** жанров и **детальная информация** о каждом жанре в \
        фильмотеке.",
    },
]

NOT_FOUND_MESSAGE = "Объект не найден."

# Настройки Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
CACHE_TTL = timedelta(minutes=5)

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "elastic")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# JWT
jwt_secret_key = os.getenv("SECRET_KEY", "buz")
jwt_algorithms = ["HS256"]
