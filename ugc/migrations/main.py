import ast
import asyncio
import sys

from aiokafka import AIOKafkaConsumer
from clickhouse_driver import Client
from clickhouse_driver.errors import Error
from loguru import logger
from models import Bookmark, Language, Rating, View, Watched
from pydantic import ValidationError

logger.add(
    sink=sys.stdout,
    format="{time} {level} {message}",
    level="INFO",
)


def insert_bookmarks(data: dict, client: Client):
    try:
        bookmark = Bookmark(**data)
        client.execute(
            "INSERT INTO default.bookmarks (user_uuid, movie_uuid, datetime, bookmarked) \
            VALUES (%(user_uuid)s, %(movie_uuid)s, %(datetime)s, %(bookmarked)s)",
            {
                "user_uuid": bookmark.user_uuid,
                "movie_uuid": bookmark.movie_uuid,
                "datetime": bookmark.datetime,
                "bookmarked": bookmark.bookmarked,
            },
        )
    except (Error, ValidationError) as e:
        logger.exception(e)


def insert_language(data: dict, client: Client):
    try:
        lang = Language(**data)
        client.execute(
            "INSERT INTO default.language (user_uuid, movie_uuid, datetime, language_movie, language_client) \
            VALUES (%(user_uuid)s, %(movie_uuid)s, %(datetime)s, %(language_movie)s, %(language_client)s)",
            {
                "user_uuid": lang.user_uuid,
                "movie_uuid": lang.movie_uuid,
                "datetime": lang.datetime,
                "language_movie": lang.language_movie,
                "language_client": lang.language_client,
            },
        )
    except (Error, ValidationError) as e:
        logger.exception(e)


def insert_ratings(data: dict, client: Client):
    try:
        rating = Rating(**data)
        client.execute(
            "INSERT INTO default.ratings (user_uuid, movie_uuid, datetime, rating) \
            VALUES (%(user_uuid)s, %(movie_uuid)s, %(datetime)s, %(rating)s)",
            {
                "user_uuid": rating.user_uuid,
                "movie_uuid": rating.movie_uuid,
                "datetime": rating.datetime,
                "rating": rating.rating,
            },
        )
    except (Error, ValidationError) as e:
        logger.exception(e)


def insert_views(data: dict, client: Client):
    try:
        view = View(**data)
        client.execute(
            "INSERT INTO default.views (user_uuid, movie_uuid, datetime, progress) \
            VALUES (%(user_uuid)s, %(movie_uuid)s, %(datetime)s, %(progress)s)",
            {
                "user_uuid": view.user_uuid,
                "movie_uuid": view.movie_uuid,
                "datetime": view.datetime,
                "progress": view.progress,
            },
        )
    except (Error, ValidationError) as e:
        logger.exception(e)


def insert_watched(data: dict, client: Client):
    try:
        watched = Watched(**data)
        client.execute(
            "INSERT INTO default.watched (user_uuid, movie_uuid, datetime, added) \
            VALUES (%(user_uuid)s, %(movie_uuid)s, %(datetime)s, %(added)s)",
            {
                "user_uuid": watched.user_uuid,
                "movie_uuid": watched.movie_uuid,
                "datetime": watched.datetime,
                "added": watched.added,
            },
        )
    except (Error, ValidationError) as e:
        logger.exception(e)


async def consume():
    consumer = AIOKafkaConsumer(
        "bookmarks",
        "language",
        "ratings",
        "views",
        "watched",
        bootstrap_servers="kafka:19092",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        auto_commit_interval_ms=1000,
        security_protocol="PLAINTEXT",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            value = ast.literal_eval(msg.value.decode("UTF-8"))
            with Client(host="clickhouse") as client:
                if msg.topic == "bookmarks":
                    insert_bookmarks(value, client)
                if msg.topic == "language":
                    insert_language(value, client)
                if msg.topic == "ratings":
                    insert_ratings(value, client)
                if msg.topic == "views":
                    insert_views(value, client)
                if msg.topic == "watched":
                    insert_watched(value, client)
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consume())
