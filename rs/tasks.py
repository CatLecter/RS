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
        logger.exception(e)


@celery_app.task
def preparer(raw_data: dict) -> tuple:
    """Задача подготовки и обогащения данных."""

    if raw_data:
        try:
            return processing(raw_data)
        except Exception as e:
            logger.exception(e)


# @celery_app.task
# def filtering(
#     bookmarks: list, ratings: list, views: list, watched: list
# ) -> List[PersonalRecommendation]:
#     """Задача коллаборативной фильтрации. Возвращает список моделей
#     PersonalRecommendation для дальнейшей их загрузки в БД.
#     """
#
#     try:
#         """Сюда должна быть интегрирована модель из LightFM."""
#         pass
#     except Exception as e:
#         logger.exception(e)


@celery_app.task
def loader(movies: List[PersonalRecommendation]) -> None:
    """Задача загрузки сгенерированных моделью данных в БД."""

    try:
        service = Loader(host=f"{cfg.rs_db_host}:{cfg.rs_db_port}")
        service.create_index()
        if movies:
            service.load(movies)
    except Exception as e:
        logger.exception(e)


@celery_app.task
def rs() -> None:
    """Конвейер последовательно выполняемых задач."""

    chain(
        getter.s(),
        preparer.s(),
        # filtering.s(),
        loader.s(),
    ).delay()


@celery_app.on_after_configure.connect
def setup_periodic_taskc(sender, **kwargs):
    """Планировщик запуска рекомендательной системы (раз в 1 минуту для теста)."""

    sender.add_periodic_task(crontab(minute="*/1"), rs.s())
