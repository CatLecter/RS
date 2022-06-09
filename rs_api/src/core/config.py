import os

PROJECT_NAME = "Recommendation System API"
PROJECT_DESCRIPTION = "API Рекомендательной Системы"
PROJECT_VERSION = "0.0.1"
PROJECT_LICENSE_INFO = {
    "name": "Apache 2.0",
    "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
}
PROJECT_TAGS_METADATA = [
    {
        "name": "Персональные рекомендации",
        "description": "**Поиск**",
    }
]

NOT_FOUND_MESSAGE = "Объект не найден."

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "rs_db")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))

# Postgres
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", 3141)
PG_HOST = os.getenv("POSTGRES_HOST", "0.0.0.0")
PG_PORT = os.getenv("POSTGRES_PORT", 5432)
PG_DB_NAME = os.getenv(
    "POSTGRES_DB",
)

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# JWT
jwt_secret_key = os.getenv("SECRET_KEY", "buz")
jwt_algorithms = ["HS256"]
