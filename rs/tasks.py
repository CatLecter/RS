from celery import Celery, chain
from celery.schedules import crontab
from clickhouse_driver import Client
from clickhouse_driver.errors import Error
from config import config as cfg
from config import log_config
from getter import EventGetter
from loguru import logger

logger.add(**log_config)

celery_app = Celery(
    "tasks",
    broker=f"amqp://{cfg.broker_user}:{cfg.broker_password}@"
    f"{cfg.broker_host}:{cfg.broker_port}",
)


@celery_app.task
def getter():
    """Задача получения данных из ClickHouse за указанный период."""
    try:
        with Client(host=f"{cfg.ch_host}") as client:
            eg = EventGetter(client)
            bookmarks = eg.get_for_period(
                period=cfg.for_period,
                table_name="bookmarks",
            )
            language = eg.get_for_period(
                period=cfg.for_period,
                table_name="language",
            )
            ratings = eg.get_for_period(
                period=cfg.for_period,
                table_name="ratings",
            )
            views = eg.get_for_period(
                period=cfg.for_period,
                table_name="views",
            )
            watched = eg.get_for_period(
                period=cfg.for_period,
                table_name="watched",
            )
            return bookmarks, language, ratings, views, watched
    except Error as e:
        logger.exception(e)


@celery_app.task
def preparer(bookmarks, language, ratings, views, watched) -> None:
    """Задача подготовки и обогащения данных."""

    if bookmarks:
        try:
            for cell in bookmarks:
                print(cell)
        except Exception as e:
            logger.exception(e)


@celery_app.task
def rs() -> None:
    """Конвейер последовательно выполняемых задач."""

    chain(
        getter.s(),
        preparer.s(),
    ).delay()


@celery_app.on_after_configure.connect
def setup_periodic_taskc(sender, **kwargs):
    """Планировщик запуска рекомендательной системы (раз в 1 минуту для теста)."""

    sender.add_periodic_task(crontab(minute="*/1"), rs.s())
