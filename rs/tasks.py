import asyncio
from typing import List

from celery import Celery, chain
from celery.schedules import crontab
from clickhouse_driver import Client
from clickhouse_driver.errors import Error
from config import TABLES
from config import config as cfg
from config import log_config
from getter import EventGetter
from loader import Loader
from loguru import logger
from ml_model import prediction_all
from models import PersonalRecommendation
from preparer import processing

logger.add(**log_config)

celery_app = Celery(
    "tasks",
    broker=f"amqp://{cfg.broker_user}:{cfg.broker_password}@"
    f"{cfg.broker_host}:{cfg.broker_port}",
)


@celery_app.task
def getter() -> dict:
    """Задача получения данных из ClickHouse за указанный период."""

    try:
        with Client(host=f"{cfg.ch_host}") as client:
            result: dict = {}
            eg = EventGetter(client)
            for table in TABLES:
                result[table] = eg.get_for_period(
                    period=cfg.for_period,
                    table_name=table,
                )
            return result
    except Error as e:
        logger.exception(f"Ошибка получения данных от ClickHouse: {e}")


@celery_app.task
def preparer(raw_data: dict) -> tuple:
    """Задача подготовки и обогащения данных."""

    if raw_data:
        try:
            return asyncio.run(processing(raw_data))
        except Exception as e:
            logger.exception(f"Ошибка подготовки данных: {e}")


@celery_app.task
def filtering(data: tuple) -> List[PersonalRecommendation]:
    """Задача коллаборативной фильтрации. Возвращает список моделей
    PersonalRecommendation для дальнейшей их загрузки в БД.
    """

    try:
        return prediction_all(data)
    except Exception as e:
        logger.exception(f"Ошибка обработки данных: {e}")


@celery_app.task
def loader(movies: List[PersonalRecommendation]) -> None:
    """Задача загрузки сгенерированных моделью данных в БД."""

    try:
        service = Loader(host=f"{cfg.rs_db_host}:{cfg.rs_db_port}")
        service.create_index()
        if movies:
            service.load(movies)
    except Exception as e:
        logger.exception(f"Ошибка загрузки данных в ElasticSearch: {e}")


@celery_app.task
def rs() -> None:
    """Конвейер последовательно выполняемых задач."""

    chain(
        getter.s(),
        preparer.s(),
        filtering.s(),
        loader.s(),
    ).delay()


@celery_app.on_after_configure.connect
def setup_periodic_taskc(sender, **kwargs):
    """Планировщик запуска рекомендательной системы (раз в 5 минуту для теста)."""

    sender.add_periodic_task(crontab(minute="*/5"), rs.s())
